import { BrowserRouter, Route, Routes } from "react-router-dom";

import { HomeRoute } from "@/routes/HomeRoute";
import { NotFoundRoute } from "@/routes/NotFoundRoute";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomeRoute />} />
        <Route path="*" element={<NotFoundRoute />} />
      </Routes>
    </BrowserRouter>
  );
}
