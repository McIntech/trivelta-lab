"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

type Health = { status: string };

export function HealthStatus() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["health"],
    queryFn: () => api<Health>("/health"),
  });

  if (isPending) {
    return <p className="text-sm text-zinc-400">Checking backend…</p>;
  }

  if (isError) {
    return (
      <p className="text-sm text-red-400">
        Backend unreachable. Start FastAPI on{" "}
        <code className="font-mono text-red-300">localhost:8000</code>.
      </p>
    );
  }

  return (
    <p className="flex items-center gap-2 text-sm text-emerald-400">
      <span className="size-2 rounded-full bg-emerald-400" />
      Backend {data.status}
    </p>
  );
}
