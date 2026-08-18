"use client";
import { HealthStatus } from "@/components/health-status";
import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import Image from "next/image";

type Sport = {
  title: string;
  order: number;
  sport_name: string;
  bg_url: string;
  tournament_id: string;
  country_code: string;
  country_name: string;
  season_id: string | null;
  display_name: string;
  logo: string;
};

export default function Home() {
  const { data } = useQuery({
    queryKey: ["sports"],
    queryFn: () => api<Sport[]>("/sports"),
  });

  const sports = data?.slice().sort((a, b) => a.order - b.order);

  console.log("sports", sports);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="flex w-full max-w-2xl flex-col items-center space-y-8">
        <nav className="flex flex-wrap justify-center gap-3">
          {sports?.map((item) => (
            <div
              key={item.tournament_id}
              className="flex w-20 flex-col items-center gap-2"
            >
              <div className="relative flex size-14 items-center justify-center overflow-hidden rounded-xl bg-zinc-800">
                <Image
                  src={item.logo}
                  alt={item.display_name}
                  width={40}
                  height={40}
                  className="object-contain"
                />
              </div>
              <span className="w-full truncate text-center text-xs text-zinc-300">
                {item.display_name}
              </span>
            </div>
          ))}
        </nav>

        <div className="w-full max-w-md space-y-6">
          <div className="space-y-2">
            <p className="text-xs font-medium tracking-[0.2em] text-zinc-500 uppercase">
              Trivelta Lab
            </p>
            <h1 className="text-3xl font-semibold tracking-tight">Sportsbook</h1>
            <p className="text-sm text-zinc-400">
              Next.js 15 · TypeScript · TanStack Query. Edit{" "}
              <code className="font-mono text-zinc-300">app/page.tsx</code> to
              start.
            </p>
          </div>
          <HealthStatus />
        </div>
      </div>
    </main>
  );
}
