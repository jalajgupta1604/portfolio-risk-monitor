/**
 * NextAuth v5 type augmentations.
 *
 * The session callback in auth.ts adds `backendToken` to the session object
 * and `backendToken`/`userId` to the JWT token. Due to the beta re-export
 * chain (next-auth -> @auth/core/types), module augmentation doesn't reliably
 * merge into the Session type used by useSession(). We use type assertions
 * in SessionSync.tsx and auth.ts callbacks instead.
 *
 * When next-auth v5 reaches stable, replace casts with proper augmentation:
 *
 *   declare module "next-auth" {
 *     interface Session { backendToken?: string }
 *     interface User { backendToken?: string }
 *   }
 */
export {};
