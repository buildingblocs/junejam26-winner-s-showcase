const externalUrlPattern = /^[a-z][a-z0-9+.-]*:/i;

export const withBase = (href: string) => {
  if (href.startsWith("#") || externalUrlPattern.test(href)) return href;

  const base = import.meta.env.BASE_URL || "/";
  const normalizedBase = base.endsWith("/") ? base : `${base}/`;

  if (href === "/") return normalizedBase;
  if (normalizedBase !== "/" && href.startsWith(normalizedBase)) return href;
  if (href.startsWith("/")) return `${normalizedBase}${href.slice(1)}`;

  return `${normalizedBase}${href}`;
};
