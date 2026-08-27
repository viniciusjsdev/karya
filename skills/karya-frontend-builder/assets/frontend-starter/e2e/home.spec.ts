import { expect, test } from "@playwright/test";

test("renders the starter experience", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /replace this starter with the product contract/i })
  ).toBeVisible();
});
