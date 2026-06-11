"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";
import { Button } from "@/components/ui/button";
import { Input, Label, Card, CardHeader, CardTitle, CardContent } from "@/components/ui/index";
import { Package, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function LoginPage() {
  const { login, isLoading } = useAuthStore();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success("Đăng nhập thành công!");
      router.push("/");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Đăng nhập thất bại");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center justify-center gap-2 font-bold text-xl mb-2">
            <Package className="h-6 w-6 text-primary" />
            ShopApp
          </Link>
          <CardTitle>Đăng nhập</CardTitle>
          <p className="text-sm text-muted-foreground">Nhập thông tin tài khoản để tiếp tục</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Mật khẩu</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Đăng nhập
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-4">
            Chưa có tài khoản?{" "}
            <Link href="/register" className="text-primary hover:underline font-medium">
              Đăng ký ngay
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
