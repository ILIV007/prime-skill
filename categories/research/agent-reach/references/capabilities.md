# Capability scope

Read this when the user asks what can be fetched, or how complete a result is. The table below states declared capabilities; it does not mean every network, account and piece of content has been verified in practice.

## Three layers

- **Public paths you can try**: the agent's own web tools, native tools or public APIs may already cover the task; no browser install or login required. Answer from the evidence actually obtained.
- **Reach fills the gaps**: the actions declared in the current release, see `agent-reach channels`. When setup is needed, first reuse the dedicated browser's saved session; only ask the user to log in in person when the chosen path actually requires login.
- **Verified on this machine**: only list the specific actions recently verified here; install, saved session and network reachability do not equal business acceptance.

## Channels in this release

| Channel | Public paths you can try | Reach additions and limits |
|---|---|---|
| GitHub | Public repos, README, issues/PRs | Repo search; reading repos/issues/PRs and returned comments; private permissions judged separately |
| YouTube | Search, titles, descriptions; native tools may get some comments and subtitle text | search/read/subtitle/transcribe; no unified comments action yet; a track list is not subtitle text; without subtitles, transcription depends on the relevant tool |
| Bilibili | Search, descriptions; some public APIs return comments and parent/child IDs | search/read/hot/subtitle; no unified comments action yet; subtitles vary by video and access path |
| Reddit | Search, body text, some comments; some public JSON may include parent/child IDs | Browser search/read/subreddit; login depends on the chosen path; does not guarantee the full comment tree or all replies; no posting comments |
| X/Twitter | Public single posts hit by search; some official public embeds return full text | search/profile/tweets/thread; a readable single post does not mean the reply stream is readable; does not guarantee the full comment tree |
| Xiaohongshu | Public lists or indexes may hold note IDs, authors, titles; empty fields must not be guessed | search/read/comments; text descriptions, top comments and loaded replies; does not guarantee all comments; does not claim to understand images/videos |
| Instagram | Some indexes and shallow homepage info; an HTML app shell is not a post | search for users, profile homepage, posts for a given user's post descriptions; no unified comments action; does not claim to understand images/videos |
| Facebook | Some indexes or HTML summaries; summaries may be truncated | search/profile; no unified details or comments action; do not treat a search summary as full text |
| LinkedIn | Search public jobs, read public JDs | jobs/read first tries the public web; only goes in-site when opencli is specified; does not guarantee all jobs are readable |
| Boss Zhipin | Search indexes may hold job summaries | search/read job lists and JDs; do not guess numbers from encoded salaries; detail fallback depends on the channel's declared capability |
| V2EX | Topics, body text and public replies | hot/node/read/user; returned scope follows this response; does not guarantee hidden or missing replies |
| Xueqiu | Some public quotes and index info | quote/search/hot_posts/hot_stocks; quote and community paths verified separately |
| Web | Agent's own search/read | Reach web search/read is an anonymous fallback; summaries, page shells and verification pages cannot stand in for full text |
| Xiaoyuzhou | Show page titles, descriptions | transcribe whole episodes to text; needs a user-provided Groq key (`agent-reach configure groq-key`) |

When talking about capabilities after login, say "can enable/try the browser actions above" — never "supports all comments after login". When the user skips login, deliver the public evidence already gathered.
