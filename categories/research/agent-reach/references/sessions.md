# Sessions and the dedicated browser

Read this when the user wants to log in, log out, or switch accounts, or when results return `NEED_LOGIN`.

## Dedicated browser

- All browser channels share one dedicated browser profile, separate from the user's everyday Chrome; the program never closes or modifies the user's everyday browser.
- The engine prefers CloakBrowser; if download or install fails, fall back to the locally installed Chrome, and remember that fallback instead of re-downloading every time. Once the network is fixed, retry with `agent-reach browser setup --retry-cloak`.
- `agent-reach add <channel>` automatically prepares Node, OpenCLI, the engine and extensions. Tools are installed at the versions tested in this release. On Windows, the Chrome fallback may need the user to click "Add to Chrome" once.
- Headless by default, no popups. Only `agent-reach login <channel>` shows a window; while the window is open, queries use that window directly instead of closing it — wait for the user to say they have logged in before querying. After the window closes, later queries go back to headless.
- Idle for 10 minutes and it closes automatically; the next call reopens it automatically. Real page actions and Reach calls reset the timer. During login it saves periodically, so the user does not need to close the window.
- Parallel is possible: at most 2 concurrent calls per platform, 4 across all platforms; extras queue, waiting at most 2 minutes, returning `BUSY` if the wait expires. At least 10 seconds between two searches on the same platform. Opening the login window, logging out, or reinstalling the browser waits for running queries to finish first.
- `agent-reach browser status` shows status, `browser setup` prepares the engine and extensions, `browser stop` closes the program-managed browser.

## Auto-reuse of existing logins

1. The first time a site is used, if the user's Chrome is connected to the OpenCLI extension, the program copies that site's login (only that site's cookies) once into the dedicated browser. It does not copy the whole browser directory, other sites, or the password store, and does not modify the source browser.
2. Once copied successfully, the saved session is reused from then on; it is not re-copied on a schedule. Cookies existing does not mean the login is valid — judge by the result of real actions.
3. When the user's Chrome is not connected to the extension, automatic reuse cannot be promised, and that cannot be taken as proof the user is not logged in; use Reach's saved session instead.
4. When several local browsers are logged in to the site: `agent-reach browser profiles` lists the sources, `agent-reach browser use <ID>` picks one — no random switching.
5. `agent-reach login <channel> --import-existing` actively re-copies that site's login once, without opening a window. If no copyable login is found, or the OpenCLI Bridge is not running, it returns `NEED_SETUP` and the saved session is unchanged.
6. Once the user has logged in personally in the dedicated window, or has run `logout` / `remove`, automatic copying stops, so a logged-out login is never revived.

## When the user must log in in person

- Only ask the user to log in when the result actually returns `NEED_LOGIN` and the remaining task genuinely needs that path. A login button beside the body text does not count as a login requirement.
- `agent-reach login <channel>` opens the dedicated browser at the site's login page; the user completes the login personally. You do not log in for them, do not ask for passwords, do not output cookies.
- If the `next` field in the returned result states follow-up steps, follow them; for some native-tool channels (e.g. Xueqiu), run `agent-reach login <channel> --sync` again after login.
- Once the user is done, re-run the original action to verify.

## Platform differences

- Boss Zhipin in-site search goes through OpenCLI and shares the dedicated browser. If job details falsely demand login because of an upstream misreport, do not make the user log in repeatedly.
- Bilibili only hands its existing login to the official Bilibili CLI tool when reading subtitles; plain search does not prepare a browser.
- Xueqiu community actions need login; sessions expire within hours, and after expiry repeat the login steps.

## Log out and delete

- `agent-reach logout <channel>`: clears that site's login and the channel's own state in the dedicated browser; other sites are kept.
- `agent-reach remove <channel>`: removes the channel and clears that site's login and storage; other sites are kept. If cleanup fails, the channel record is kept and an error is returned; the user can retry.
- After either one, that site's login is no longer auto-copied.
