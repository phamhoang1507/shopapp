import Navbar from "@/components/layout/Navbar";

export default function StoreLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-6">
        {children}
      </main>
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        © 2026 ShopApp. All rights reserved.
      </footer>
    </div>
  );
}
