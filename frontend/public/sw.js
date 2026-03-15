/* Service worker for Web Push - go! PWA */

self.addEventListener("push", (event) => {
  if (!event.data) return;

  let data;
  try {
    data = event.data.json();
  } catch {
    data = { title: "go!", body: event.data.text() || "New opportunity" };
  }

  const title = data.title || "go!";
  const body = data.body || "You have a new opportunity";
  const activationId = data.activation_id || data.activationId;
  const url = activationId ? `/activation/${activationId}` : "/dashboard";

  const options = {
    body,
    icon: "/icon.svg",
    badge: "/icon.svg",
    tag: activationId || "activation",
    data: { url, activationId },
    requireInteraction: true,
    actions: [
      { action: "open", title: "View" },
      { action: "dismiss", title: "Later" },
    ],
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const url = event.notification.data?.url || "/dashboard";

  event.waitUntil(
    clients.matchAll({ type: "window", includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && "focus" in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});
