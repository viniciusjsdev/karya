import { screen } from "@testing-library/react";

import { renderWithAppProviders } from "@/test/render";
import { HomePage } from "./HomePage";

describe("HomePage", () => {
  it("renders the starter handoff", async () => {
    renderWithAppProviders(<HomePage />);

    expect(
      await screen.findByRole("heading", {
        name: /replace this starter with the product contract/i
      })
    ).toBeInTheDocument();
  });
});
