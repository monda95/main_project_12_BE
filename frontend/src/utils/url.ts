export const buildUrl = (
  baseUrl: string,
  path: string,
  query?: Record<string, string | number | boolean | undefined>
) => {
  const url = new URL(path, baseUrl);

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === null) return;
      url.searchParams.set(key, String(value));
    });
  }

  return url.toString();
};
