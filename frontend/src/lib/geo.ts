/**
 * Browser geolocation wrapper
 */

export interface GeoPosition {
  lat: number;
  lng: number;
  accuracy?: number;
}

export type GeoPermissionState = "granted" | "denied" | "prompt";

export interface GeoError {
  code: number;
  message: string;
}

export function getPermissionState(): GeoPermissionState | null {
  if (typeof navigator === "undefined" || !navigator.permissions) return null;
  return null; // permissions.query not available for geolocation in all browsers
}

export function isGeolocationSupported(): boolean {
  return typeof navigator !== "undefined" && "geolocation" in navigator;
}

export function getCurrentPosition(): Promise<GeoPosition> {
  return new Promise((resolve, reject) => {
    if (!isGeolocationSupported()) {
      reject({ code: -1, message: "Geolocation is not supported" });
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
        });
      },
      (err) => {
        reject({
          code: err.code,
          message:
            err.code === 1
              ? "Permission denied"
              : err.code === 2
                ? "Position unavailable"
                : err.code === 3
                  ? "Request timeout"
                  : err.message,
        });
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  });
}

export function watchPosition(
  onSuccess: (pos: GeoPosition) => void,
  onError?: (err: GeoError) => void
): number | null {
  if (!isGeolocationSupported()) {
    onError?.({ code: -1, message: "Geolocation is not supported" });
    return null;
  }

  const id = navigator.geolocation.watchPosition(
    (pos) =>
      onSuccess({
        lat: pos.coords.latitude,
        lng: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
      }),
    (err) =>
      onError?.({
        code: err.code,
        message: err.message,
      }),
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 30000,
    }
  );

  return id;
}

export function clearWatch(id: number): void {
  if (typeof navigator !== "undefined" && "geolocation" in navigator) {
    navigator.geolocation.clearWatch(id);
  }
}
