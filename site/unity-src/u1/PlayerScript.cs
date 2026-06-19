using System.Collections;
using Unity.Mathematics;
using UnityEngine;
using UnityEngine.InputSystem;

public class PlayerScript : MonoBehaviour
{
    public enum Form { Paper, Ball, Plane }

    [Header("Paper (Z)")]
    public float runSpeed = 14f;
    public float runAccel = 100f;
    public float airAccel = 70f;
    public float jumpSpeed = 16f;
    public float paperGravity = 2.6f;
    public float coyoteTime = 0.12f;
    public float jumpBufferTime = 0.12f;
    public bool doubleJumpUnlocked = true;

    [Header("Ball (X)")]
    public float ballGravity = 2f;
    public float ballForce = 80f;
    public float ballSelfSpeed = 14f;  // fastest the player can drive the ball unaided
    public float ballMaxSpeed = 26f;   // hard cap (ramp/gravity fed)

    [Header("Plane (C, air only)")]
    public float planeGravity = 0.5f;
    public float planeBoost = 14f;
    public float planeTopSpeed = 18f;
    public float planeSteer = 14f;
    public float planeMaxFall = 3f;    // gentle sink at full speed
    public float planeStallFall = 9f;  // fall rate when too slow
    public float planeJumpBoost = 5f;  // air jump while gliding = slight boost

    [Header("Visuals")]
    public float foldTime = 0.12f;

    public Form form { get; private set; } = Form.Paper;

    const int GroundMask = 1 << 0; // world geometry lives on Default; player on Ignore Raycast

    static readonly Vector3 PaperSize = new Vector3(1f, 1.5f, 0.6f);
    static readonly Vector3 PlaneSize = new Vector3(1.5f, 0.5f, 0.6f);
    // hitbox is tighter than the 1-unit sprite so the ball threads gaps the paper can't
    const float BallRadius = 0.4f;

    Rigidbody rb;
    PlayerInput input;
    BoxCollider paperCol;
    SphereCollider ballCol;
    BoxCollider planeCol;
    SpriteRenderer sr;
    Transform visual;

    Sprite[] paperIdle, paperWalk, paperFold, ballFrames, planeFrames;

    int jumpZoneCount;
    Vector3 respawnPoint;

    bool grounded;
    float lastGroundedTime = -99f;
    float jumpPressedTime = -99f;
    const int MaxJumps = 2;        // ground jump + one air jump
    int jumpsLeft = MaxJumps;      // refilled on landing; not consumed inside a JumpZone
    int facing = 1;
    float animClock;
    float foldTimer;
    Coroutine squashRoutine;

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        input = GetComponent<PlayerInput>();
        respawnPoint = transform.position;

        // overlap probes must not see the player itself
        gameObject.layer = 2; // Ignore Raycast

        // gravity is applied manually so each form gets its own scale
        rb.useGravity = false;

        // replace whatever placeholder collider the scene has with the form colliders
        foreach (Collider c in GetComponents<Collider>())
        {
            c.enabled = false;
        }

        // The ball is a near-frictionless slider: gravity accelerates it down
        // ramps with no fuss, and with no surface grip it can never crawl up
        // a vertical wall. The rolling look is faked on the Visual transform.
        PhysicsMaterial ballMat = new PhysicsMaterial("ball")
        {
            dynamicFriction = 0.02f, staticFriction = 0.02f, bounciness = 0.05f,
            frictionCombine = PhysicsMaterialCombine.Minimum
        };
        PhysicsMaterial paperMat = new PhysicsMaterial("paper")
        {
            dynamicFriction = 0f, staticFriction = 0f, bounciness = 0f,
            frictionCombine = PhysicsMaterialCombine.Minimum // no wall-sticking
        };

        paperCol = gameObject.AddComponent<BoxCollider>();
        paperCol.size = PaperSize;
        paperCol.material = paperMat;
        ballCol = gameObject.AddComponent<SphereCollider>();
        ballCol.radius = BallRadius;
        ballCol.material = ballMat;
        planeCol = gameObject.AddComponent<BoxCollider>();
        planeCol.size = PlaneSize;
        planeCol.material = paperMat;

        paperIdle = LoadFrames("paper_idle_0", "paper_idle_1");
        paperWalk = LoadFrames("paper_walk_0", "paper_walk_1");
        paperFold = LoadFrames("paper_fold_0", "paper_fold_1");
        ballFrames = LoadFrames("ball_0", "ball_1", "ball_2", "ball_3");
        planeFrames = LoadFrames("plane_0", "plane_1");

        sr = GetComponentInChildren<SpriteRenderer>();
        if (sr == null)
        {
            // scene still has a placeholder mesh visual; hide it and add a sprite child
            foreach (MeshRenderer mr in GetComponentsInChildren<MeshRenderer>())
            {
                mr.enabled = false;
            }
            GameObject go = new GameObject("Visual");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = new Vector3(0, 0, -0.6f);
            sr = go.AddComponent<SpriteRenderer>();
        }
        visual = sr.transform;

        ApplyForm(Form.Paper, instant: true);
    }

    static Sprite[] LoadFrames(params string[] names)
    {
        Sprite[] frames = new Sprite[names.Length];
        for (int i = 0; i < names.Length; i++)
        {
            frames[i] = Resources.Load<Sprite>("Player/" + names[i]);
        }
        return frames;
    }

    void Update()
    {
        InputAction jump = input.actions["Jump"];
        if (jump.WasPressedThisFrame())
        {
            jumpPressedTime = Time.time;
        }
        if (jump.WasReleasedThisFrame() && form == Form.Paper && rb.linearVelocity.y > 0)
        {
            // variable jump height: let go early for a short hop
            Vector3 v = rb.linearVelocity;
            v.y *= 0.5f;
            rb.linearVelocity = v;
        }

        Keyboard kb = Keyboard.current;
        if (kb != null)
        {
            if (kb.xKey.wasPressedThisFrame && form != Form.Ball) TrySetForm(Form.Ball);
            if (kb.zKey.wasPressedThisFrame && form != Form.Paper) TrySetForm(Form.Paper);
            if (kb.cKey.wasPressedThisFrame && form != Form.Plane && !grounded) TrySetForm(Form.Plane);
        }

        Animate();
    }

    void FixedUpdate()
    {
        grounded = CheckGrounded();
        if (grounded)
        {
            lastGroundedTime = Time.time;
            jumpsLeft = MaxJumps;
        }

        rb.AddForce(Physics.gravity * GravityScale(), ForceMode.Acceleration);

        float move = input.actions["Move"].ReadValue<float>();
        if (move != 0)
        {
            facing = move > 0 ? 1 : -1;
        }

        switch (form)
        {
            case Form.Paper: TickPaper(move); break;
            case Form.Ball: TickBall(move); break;
            case Form.Plane: TickPlane(move); break;
        }
    }

    float GravityScale()
    {
        return form == Form.Ball ? ballGravity : form == Form.Plane ? planeGravity : paperGravity;
    }

    void TickPaper(float move)
    {
        Vector3 v = rb.linearVelocity;
        float accel = grounded ? runAccel : airAccel;
        v.x = Mathf.MoveTowards(v.x, move * runSpeed, accel * Time.fixedDeltaTime);

        bool wantsJump = Time.time - jumpPressedTime < jumpBufferTime;
        if (wantsJump)
        {
            bool inZone = jumpZoneCount > 0;
            bool canCoyote = Time.time - lastGroundedTime < coyoteTime;
            bool groundJump = canCoyote || inZone;
            bool airJump = !groundJump && doubleJumpUnlocked && jumpsLeft > 0;
            if (groundJump || airJump)
            {
                v.y = airJump ? jumpSpeed * 0.95f : jumpSpeed;
                if (!inZone) // zone jumps are free
                {
                    jumpsLeft = groundJump ? MaxJumps - 1 : jumpsLeft - 1;
                }
                jumpPressedTime = -99f;
                lastGroundedTime = -99f;
                Squash(airJump ? 0.75f : 0.7f, airJump ? 1.2f : 1.25f);
            }
        }
        rb.linearVelocity = v;
    }

    void TickBall(float move)
    {
        Vector3 v = rb.linearVelocity;
        // Player effort only works below ballSelfSpeed (or when braking);
        // anything faster has to be earned by rolling downhill.
        bool braking = move != 0 && Mathf.Sign(move) != Mathf.Sign(v.x);
        if (braking || Mathf.Abs(v.x) < ballSelfSpeed)
        {
            rb.AddForce(new Vector3(move * ballForce, 0f, 0f));
        }
        v = rb.linearVelocity;
        if (Mathf.Abs(v.x) > ballMaxSpeed)
        {
            v.x = Mathf.Sign(v.x) * ballMaxSpeed;
            rb.linearVelocity = v;
        }
        // balls cannot jump — that's the whole point
    }

    void TickPlane(float move)
    {
        Vector3 v = rb.linearVelocity;
        if (move != 0)
        {
            v.x = Mathf.MoveTowards(v.x, move * planeTopSpeed, planeSteer * Time.fixedDeltaTime);
        }

        // double jump while gliding = slight boost instead of a hop
        bool wantsJump = Time.time - jumpPressedTime < jumpBufferTime;
        if (wantsJump && doubleJumpUnlocked && (jumpsLeft > 0 || jumpZoneCount > 0))
        {
            if (jumpZoneCount == 0) // zone jumps are free
            {
                jumpsLeft--;
            }
            jumpPressedTime = -99f;
            v.y = Mathf.Max(v.y, 3.5f);
            v.x = Mathf.Clamp(v.x + facing * planeJumpBoost, -planeTopSpeed, planeTopSpeed);
            Squash(1.2f, 0.8f);
        }

        // lift scales with airspeed: fast = gentle sink, slow = stall
        float speed01 = Mathf.Clamp01(Mathf.Abs(v.x) / (planeBoost * 0.85f));
        float maxFall = Mathf.Lerp(planeStallFall, planeMaxFall, speed01);
        if (v.y < -maxFall)
        {
            v.y = Mathf.MoveTowards(v.y, -maxFall, 30f * Time.fixedDeltaTime);
        }
        rb.linearVelocity = v;

        if (grounded)
        {
            TrySetForm(Form.Paper); // landing auto-unfolds
        }
    }

    public bool TrySetForm(Form next)
    {
        if (next == form)
        {
            return true;
        }
        if (next == Form.Paper && !RoomToUnfold())
        {
            Squash(1.15f, 0.85f); // bump: no room to unfold here
            return false;
        }
        ApplyForm(next, instant: false);
        return true;
    }

    void ApplyForm(Form next, bool instant)
    {
        // lift slightly when growing a downward extent so we don't clip the floor
        if (!instant && next == Form.Paper && form != Form.Paper && grounded)
        {
            transform.position += Vector3.up * UnfoldLift();
        }

        form = next;
        paperCol.enabled = next == Form.Paper;
        ballCol.enabled = next == Form.Ball;
        planeCol.enabled = next == Form.Plane;

        // frictionless ball still coasts to a stop
        rb.linearDamping = next == Form.Ball ? 0.35f : 0f;

        if (next == Form.Plane)
        {
            Vector3 v = rb.linearVelocity;
            int dir = v.x != 0 ? (int)Mathf.Sign(v.x) : facing;
            v.x = Mathf.Max(Mathf.Abs(v.x), planeBoost) * dir; // momentum boost on unfolding wings
            if (v.y < 0)
            {
                v.y *= 0.4f;
            }
            rb.linearVelocity = v;
            facing = dir;
        }

        if (visual != null)
        {
            visual.localRotation = Quaternion.identity;
            // keep the sprite's bottom on the collider's bottom (ball hitbox is smaller than its sprite)
            Vector3 lp = visual.localPosition;
            lp.y = next == Form.Ball ? 0.5f - BallRadius : 0f;
            visual.localPosition = lp;
        }
        if (!instant)
        {
            foldTimer = foldTime;
            Squash(1.25f, 0.75f);
        }
    }

    float UnfoldLift()
    {
        // current form's bottom is shallower than paper's; raise so bottoms line up
        float halfHeight = form == Form.Ball ? BallRadius : PlaneSize.y / 2f;
        return PaperSize.y / 2f - halfHeight + 0.03f;
    }

    bool RoomToUnfold()
    {
        Vector3 center = transform.position;
        if (form != Form.Paper && grounded)
        {
            center.y += UnfoldLift();
        }
        return !Physics.CheckBox(center, PaperSize * 0.95f / 2f, Quaternion.identity,
            GroundMask, QueryTriggerInteraction.Ignore);
    }

    bool CheckGrounded()
    {
        Bounds b = ActiveCollider().bounds;
        float z = transform.position.z;
        float startY = b.min.y + 0.1f;
        float castDistance = 0.2f; // checks up to 0.1f below the bottom of the collider

        // Check three points: left edge, center, right edge
        // We use 0.9f of the extents to ensure coverage close to the corners (essential for slopes)
        // while avoiding wall-climbing behavior on vertical walls.
        float leftX = b.center.x - b.extents.x * 0.9f;
        float centerX = b.center.x;
        float rightX = b.center.x + b.extents.x * 0.9f;

        Vector3 leftOrigin = new Vector3(leftX, startY, z);
        Vector3 centerOrigin = new Vector3(centerX, startY, z);
        Vector3 rightOrigin = new Vector3(rightX, startY, z);

        bool leftHit = Physics.Raycast(leftOrigin, Vector3.down, castDistance, GroundMask, QueryTriggerInteraction.Ignore);
        bool centerHit = Physics.Raycast(centerOrigin, Vector3.down, castDistance, GroundMask, QueryTriggerInteraction.Ignore);
        bool rightHit = Physics.Raycast(rightOrigin, Vector3.down, castDistance, GroundMask, QueryTriggerInteraction.Ignore);

        // Debug visualization in scene view during play mode
        Debug.DrawRay(leftOrigin, Vector3.down * castDistance, leftHit ? Color.green : Color.red);
        Debug.DrawRay(centerOrigin, Vector3.down * castDistance, centerHit ? Color.green : Color.red);
        Debug.DrawRay(rightOrigin, Vector3.down * castDistance, rightHit ? Color.green : Color.red);

        return leftHit || centerHit || rightHit;
    }

    Collider ActiveCollider()
    {
        if (ballCol.enabled) return ballCol;
        if (planeCol.enabled) return planeCol;
        return paperCol;
    }

    void Animate()
    {
        if (sr == null)
        {
            return;
        }
        animClock += Time.deltaTime;
        sr.flipX = facing < 0;

        if (foldTimer > 0)
        {
            foldTimer -= Time.deltaTime;
            sr.sprite = paperFold[foldTimer > foldTime * 0.5f ? 0 : 1];
            return;
        }

        Vector3 v = rb.linearVelocity;
        switch (form)
        {
            case Form.Paper:
                if (!grounded)
                    sr.sprite = paperWalk[1];
                else if (Mathf.Abs(v.x) > 0.5f)
                    sr.sprite = paperWalk[(int)(animClock * 8f) % paperWalk.Length];
                else
                    sr.sprite = paperIdle[(int)(animClock * 1.6f) % paperIdle.Length];
                break;
            case Form.Ball:
                sr.sprite = ballFrames[0];
                // fake the roll: spin the visual to match ground speed (0.5 = sprite radius, not hitbox)
                visual.Rotate(0f, 0f, -v.x / 0.5f * Mathf.Rad2Deg * Time.deltaTime);
                break;
            case Form.Plane:
                sr.sprite = planeFrames[v.y < -3f ? 1 : 0];
                float tilt = Mathf.Clamp(Mathf.Atan2(v.y, Mathf.Abs(v.x)) * Mathf.Rad2Deg, -35f, 25f);
                visual.localRotation = Quaternion.Euler(0, 0, facing > 0 ? tilt : -tilt);
                break;
        }
    }

    void Squash(float sx, float sy)
    {
        if (visual == null || !isActiveAndEnabled)
        {
            return;
        }
        if (squashRoutine != null)
        {
            StopCoroutine(squashRoutine);
        }
        squashRoutine = StartCoroutine(SquashRoutine(sx, sy));
    }

    IEnumerator SquashRoutine(float sx, float sy)
    {
        Vector3 target = new Vector3(sx, sy, 1f);
        visual.localScale = target;
        float t = 0f;
        while (t < 0.18f)
        {
            t += Time.deltaTime;
            visual.localScale = Vector3.Lerp(target, Vector3.one, t / 0.18f);
            yield return null;
        }
        visual.localScale = Vector3.one;
    }

    public void EnterJumpZone()
    {
        jumpZoneCount++;
    }

    public void ExitJumpZone()
    {
        jumpZoneCount = math.max(0, jumpZoneCount - 1);
    }

    public void SetCheckpoint(Vector3 point)
    {
        respawnPoint = point;
    }

    public void Respawn()
    {
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        rb.position = respawnPoint;
        transform.position = respawnPoint;
        ApplyForm(Form.Paper, instant: true);
        foldTimer = 0f;
        if (visual != null)
        {
            visual.localScale = Vector3.one;
            visual.localRotation = Quaternion.identity;
        }
        jumpPressedTime = -99f;
        jumpsLeft = MaxJumps;
    }
}
