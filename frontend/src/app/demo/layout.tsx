export default function DemoLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="demo-soft demo-bg fixed inset-0 z-50 flex flex-col overflow-visible">
      {children}
    </div>
  );
}
