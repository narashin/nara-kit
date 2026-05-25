import Link from "next/link";
import { CATEGORY_LABELS } from "@/lib/tarot/spreads";

export default function LandingPage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-10 px-6 py-16 text-center">
      <div className="flex flex-col items-center gap-4">
        <div className="text-6xl" aria-hidden>
          🔮
        </div>
        <h1 className="text-4xl font-bold tracking-tight">덕운</h1>
        <p className="max-w-sm text-balance text-zinc-400">
          최애와 나의 케미, 입덕운, 영업운까지.
          <br />
          덕질하는 사람을 위한 타로.
        </p>
      </div>

      <ul className="flex flex-wrap justify-center gap-2 text-sm text-zinc-300">
        {Object.values(CATEGORY_LABELS).map((label) => (
          <li
            key={label}
            className="rounded-full border border-white/10 bg-white/5 px-3 py-1"
          >
            {label}
          </li>
        ))}
      </ul>

      <Link
        href="/login"
        className="rounded-full bg-[#f5d76e] px-8 py-3 font-semibold text-[#0b0a1a] transition hover:brightness-110"
      >
        시작하기
      </Link>

      <p className="text-xs text-zinc-600">Wave 0 · 인프라 셋업 완료</p>
    </main>
  );
}
