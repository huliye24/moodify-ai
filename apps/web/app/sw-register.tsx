"use client";

import { useEffect } from "react";

export default function SwRegister() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    void navigator.serviceWorker.register("/sw.js").catch(() => {
      // SW unsupported or blocked — PWA installability degrades, app still works
    });
  }, []);
  return null;
}
