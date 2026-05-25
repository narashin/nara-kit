import Link from "next/link";

export const metadata = { title: "로그인" };

export default function LoginPage() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-8 px-6 py-16 text-center">
      <h1 className="text-2xl font-bold">로그인</h1>
      <p className="max-w-xs text-zinc-400">
        Google 로그인은 Wave 1에서 연결됩니다.
        <br />
        (Firebase Auth 셋업 후)
      </p>
      <button
        type="button"
        disabled
        className="cursor-not-allowed rounded-full border border-white/15 bg-white/5 px-6 py-3 text-zinc-500"
      >
        Google로 계속하기 (준비 중)
      </button>
      <Link href="/" className="text-sm text-zinc-500 underline">
        ← 돌아가기
      </Link>
    </main>
  );
}
