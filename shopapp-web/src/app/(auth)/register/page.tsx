"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";
import { Button } from "@/components/ui/button";
import { Input, Label, Card, CardHeader, CardTitle, CardContent } from "@/components/ui/index";
import { Package, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function RegisterPage() {
  const { register, isLoading } = useAuthStore();
  const router = useRouter();
  const [form, setForm] = useState({ email: "", full_name: "", password: "", confirm: "" });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirm) { toast.error("Mật khẩu xác nhận không khớp"); return; }
    if (form.password.length < 6) { toast.error("Mật khẩu tối thiểu 6 ký tự"); return; }
    try {
      await register(form.email, form.full_name, form.password);
      toast.success("Đăng ký thành công!");
      router.push("/");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Đăng ký thất bại");
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
          <CardTitle>Tạo tài khoản</CardTitle>
          <p className="text-sm text-muted-foreground">Điền thông tin để đăng ký</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Họ và tên</Label>
              <Input placeholder="Nguyễn Văn A" value={form.full_name} onChange={(e) => setForm({...form, full_name: e.target.value})} required />
            </div>
            <div className="space-y-2">
              <Label>Email</Label>
              <Input type="email" placeholder="email@example.com" value={form.email} onChange={(e) => setForm({...form, email: e.target.value})} required />
            </div>
            <div className="space-y-2">
              <Label>Mật khẩu</Label>
              <Input type="password" placeholder="Tối thiểu 6 ký tự" value={form.password} onChange={(e) => setForm({...form, password: e.target.value})} required />
            </div>
            <div className="space-y-2">
              <Label>Xác nhận mật khẩu</Label>
              <Input type="password" placeholder="Nhập lại mật khẩu" value={form.confirm} onChange={(e) => setForm({...form, confirm: e.target.value})} required />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Đăng ký
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-4">
            Đã có tài khoản?{" "}
            <Link href="/login" className="text-primary hover:underline font-medium">Đăng nhập</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
