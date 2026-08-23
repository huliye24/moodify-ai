import { redirect } from "next/navigation";

/** Compatibility only: `/t/[id]` is the single authoritative track surface. */
export default async function LegacyTrackPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  redirect(`/t/${encodeURIComponent(id)}`);
}
