// app.config.js — dynamic Expo config that pulls settings from environment variables.
// Avoid importing runtime-only dependencies like `dotenv` here so EAS can evaluate
// this file without requiring local dev dependencies.

const backendUrl = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://api.example.com';

export default ({ config }) => ({
  ...config,
  extra: {
    ...(config.extra || {}),
    backendUrl,
  },
});
