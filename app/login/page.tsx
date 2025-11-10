"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import anime from "animejs/lib/anime.es.js";
import styles from "./login.module.css";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Icons } from "@/components/icons";
import { cn } from "@/lib/utils";

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false);
  const bgRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const container = bgRef.current;
    if (!container) return;

    const shapes = Array.from(container.querySelectorAll(".shape"));

    // Animate each shape with a slightly different randomized path
    const animations = shapes.map((el, i) =>
      anime({
        targets: el,
        translateX: () => anime.random(-40, 40),
        translateY: () => anime.random(-30, 30),
        rotate: () => anime.random(-180, 180),
        scale: () => anime.random(0.8, 1.4),
        opacity: () => anime.random(0.08, 0.22),
        duration: () => anime.random(2800, 5200),
        easing: "easeInOutSine",
        direction: "alternate",
        loop: true,
        delay: i * 60,
      })
    );

    return () => {
      animations.forEach((a) => a.pause());
      anime.remove(shapes);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      // TODO: integrate with real login API
      await new Promise((r) => setTimeout(r, 900));
      alert("Logged in (demo)");
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Render a bunch of shapes to animate
  const shapeTypes = ["circle", "square", "triangle"] as const;
  const SHAPE_COUNT = 28;

  return (
    <div className={cn(styles.page, styles.theme)}>
      <div ref={bgRef} className={styles.bg}>
        {Array.from({ length: SHAPE_COUNT }).map((_, i) => {
          const type = shapeTypes[i % shapeTypes.length];
          const left = `${Math.floor(Math.random() * 100)}%`;
          const top = `${Math.floor(Math.random() * 100)}%`;
          return (
            <div
              key={i}
              className={cn("shape", styles.shape, styles[type])}
              style={{ left, top }}
            />
          );
        })}
      </div>

      <div className={styles.card}>
        <div className={styles.header}>
          <Icons.logo className="mx-auto h-6 w-6 text-white/90" />
          <h1 className={styles.title}>Welcome back</h1>
          <p className={styles.subtitle}>Sign in to continue</p>
        </div>
        <div className={styles.body}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="email" className="text-slate-200">Email</Label>
              <Input id="email" name="email" type="email" className={styles.input} required />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password" className="text-slate-200">Password</Label>
              <Input id="password" name="password" type="password" className={styles.input} required />
            </div>
            <Button type="submit" disabled={isLoading} className={styles.button}>
              {isLoading ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </div>
        <div className={styles.footer}>
          <Link href="/auth/forgot" className={styles.link}>Forgot your password?</Link>
          <div className="mt-2 text-sm text-slate-400">
            Or <Link href="/login" className="underline">use OAuth</Link>
          </div>
        </div>
      </div>

      <Link
        href="/"
        className={cn(
          "absolute left-4 top-4 inline-flex items-center text-slate-300 hover:text-white",
          "transition-colors"
        )}
      >
        <Icons.chevronLeft className="mr-2 h-4 w-4" /> Back
      </Link>
    </div>
  );
}