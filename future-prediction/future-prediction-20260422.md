# 予測検証レポート 2026-04-22

対象：過去1週間（4/19〜4/21、今日 4/22 を除く）の `report/*.md` の **Future** セクションと、今日（2026-04-22）付 `news-20260422.md` の内容との関連を確認。併せてユーザー提示の 2 予測との関連も照合。

## Checking Predictions Against Reality

### Table

Relevance（5段階）: 5=非常に高い / 4=高い / 3=中 / 2=低い / 1=関連弱い or 反対方向

| Prediction (summary) | Prediction date | Related item(s) in today's report (20260422) | Relevance | Reference link(s) |
|---|---|---|---|---|
| 1-bit ネイティブ学習が主流の量子化代替に（Bonsai 系牽引、Qwen/Llama 1-bit 派生が続く） | 2026-04-19 | Bonsai-8B（1.15GB, RTX4090 で 6 倍速・4-5 倍省エネ）の Hugging Face GGUF / MLX 公開、llama.cpp が 1-bit フォーマットを直接サポート、MarkTechPost の実装チュートリアル | 4 | [MarkTechPost - Bonsai 1-Bit LLM on CUDA](https://www.marktechpost.com/2026/04/18/a-coding-tutorial-for-running-prismml-bonsai-1-bit-llm-on-cuda-with-gguf-benchmarking-chat-json-and-rag/) / [Hugging Face - Bonsai-8B-gguf](https://huggingface.co/prism-ml/Bonsai-8B-gguf) |
| 「Agent Registry」方式への収斂（スキル・ツール権限・監査トレースを配布するレジストリ標準） | 2026-04-19 | Ollama v0.21.1-rc0 の `ollama launch` による OpenClaw / Hermes / Copilot CLI 統合（前回 v0.21.0 から継続）、OpenClaw 2026.4.20 の `OPENCLAW_*` env 鍵ブロックと paired-device セッションスコープ厳格化、Hermes の OSV ベース MCP 拡張マルウェアスキャン、NemoClaw「外側ラッパー」戦略の再評価 | 3 | [GitHub - openclaw v2026.4.20](https://github.com/openclaw/openclaw/releases/tag/v2026.4.20) / [DEV - Hermes Agent Review](https://dev.to/tokenmixai/hermes-agent-review-956k-stars-self-improving-ai-agent-april-2026-11le) / [NVIDIA Docs - NemoClaw](https://docs.nvidia.com/nemoclaw/latest/index.html) |
| 間接プロンプトインジェクションが CVE の主カテゴリ化（CVSS 8.0+ の LLM 連携 CVE が常連化） | 2026-04-19 | OpenClaw CVE-2026-41329（CVSS 9.9、サンドボックス回避→権限昇格）Apr 21 公開、SGLang CVE-2026-5760（CVSS 9.8）報道継続、Vercel CEO が AI 補助攻撃に言及、ESET NGate マルウェアの AI 生成疑惑 | 5 | [The Hacker Wire - CVE-2026-41329](https://www.thehackerwire.com/openclaw-sandbox-bypass-leads-to-privilege-escalation-cve-2026-41329/) / [The Hacker News - SGLang CVE-2026-5760](https://thehackernews.com/2026/04/sglang-cve-2026-5760-cvss-98-enables.html) / [The Register - Vercel AI-driven](https://www.theregister.com/2026/04/21/vercel_ceo_points_to_aidriven/) |
| 「ローカル > クラウド」逆転の加速（2026 Q3 までに個人/SMB 向けエージェントはローカル既定が標準化） | 2026-04-20 | Hugging Face ml-intern が Qwen3-1.7B の GPQA を 10 時間未満で 8.5%→32% に引き上げ、Claude Code 22.99% を上回る。Bonsai-8B / llama.cpp 1-bit 直接ロード、Qwen3.6-35B-A3B の再評価継続 | 5 | [MarkTechPost - ml-intern](https://www.marktechpost.com/2026/04/21/hugging-face-releases-ml-intern-an-open-source-ai-agent-that-automates-the-llm-post-training-workflow/) / [GitHub - QwenLM/Qwen3.6](https://github.com/QwenLM/Qwen3.6) |
| CI/エージェントへの Secret 流出が次の主戦場（「Agent-in-the-Loop Secret Exfiltration」が CIS/OWASP トップリスクへ） | 2026-04-20 | Vercel–Context.ai サプライチェーン侵害（Context.ai の Google Workspace OAuth トークン侵害 → Vercel 内部環境 → BreachForums $2M 出品）、Vercel CEO の AI 補助攻撃への言及、OpenClaw サンドボックス回避 CVE | 5 | [The Hacker News - Vercel Breach Tied to Context AI](https://thehackernews.com/2026/04/vercel-breach-tied-to-context-ai-hack.html) / [TechCrunch - Vercel security incident](https://techcrunch.com/2026/04/20/app-host-vercel-confirms-security-incident-says-customer-data-was-stolen-via-breach-at-context-ai/) |
| "Headless Everything" アーキテクチャの標準化（MCP/Agent Registry 上に headless 優先メタデータ） | 2026-04-20 | 直接の進展は薄い。むしろ逆方向：OpenAI Codex が `computer use / web workflows / image gen / in-app browsing` へ拡張、ChatGPT Images 2.0 の UI 多重化でマルチ UI 同一推論予算へ舵 | 2 | [The New Stack - ChatGPT Images 2.0](https://thenewstack.io/chatgpt-images-20-openai/) / [9to5Mac - OpenAI Codex expansion](https://9to5mac.com/2026/04/21/openai-teases-next-ai-announcement-coming-today-heres-what-to-expect/) |
| 「GGUF 供給経路」がサプライチェーン攻撃の新しい主戦場（HF/Ollama/ModelScope が chat_template 署名検証を標準化） | 2026-04-21 | SGLang CVE-2026-5760 の報道継続（悪意 GGUF の tokenizer.chat_template 経由 RCE）、Bonsai-8B GGUF の HF 公開と llama.cpp 直接ロード（供給経路の拡大）。ただし GGUF 向け署名検証の標準化アナウンスは本日分では未確認 | 3 | [The Hacker News - SGLang CVE-2026-5760](https://thehackernews.com/2026/04/sglang-cve-2026-5760-cvss-98-enables.html) / [Hugging Face - Bonsai-8B-gguf](https://huggingface.co/prism-ml/Bonsai-8B-gguf) |
| 「ハイパースケーラ × フロンティアラボの排他同盟」時代（5極体制の固定化） | 2026-04-21 | Amazon–Anthropic の $25B 投資後続報道：100,000+ 組織が Bedrock で Claude 利用、Q2 2026 から 5GW 稼働開始、Anthropic が $100B / 10 年を AWS コミット。Claude Mythos Preview は Project Glasswing 提携（AWS/Apple/Google/JPMC/Microsoft/NVIDIA）限定 | 5 | [Cyberpress - Amazon Anthropic 5GW](https://cyberpress.org/amazon-and-anthropic-deepen/) / [AISI - Claude Mythos Preview evaluation](https://www.aisi.gov.uk/blog/our-evaluation-of-claude-mythos-previews-cyber-capabilities) |
| プロプライエタリ再膨張とオープンウェイトの地政学分断（「最強モデル＝非オープンウェイト」が明確化） | 2026-04-21 | Qwen3.6-Max-Preview のホステッド専用継続、Claude Mythos Preview の提携企業限定ゲーティング、オープンウェイト側は Qwen3.6-35B-A3B と Bonsai 中心。ローカル=実用帯／クラウド=フロンティアの線引き | 4 | [buildfastwithai - Qwen3.6-Max-Preview](https://www.buildfastwithai.com/blogs/qwen3-6-max-preview-review-2026) / [AISI - Claude Mythos Preview evaluation](https://www.aisi.gov.uk/blog/our-evaluation-of-claude-mythos-previews-cyber-capabilities) |

### Summary of Findings

過去3日の Future セクション 9 予測中、**Relevance 4 以上が 6 件、3 が 2 件、2 が 1 件**。全体として「間接プロンプトインジェクションの主 CVE カテゴリ化」「ローカル > クラウド逆転」「CI/エージェント Secret 流出」「ハイパースケーラ排他同盟」の 4 件は、**わずか 1〜3 日で新規具体事例（CVE、侵害、投資、ベンチ超え）が出揃い**、実態追認フェーズに入った。

「Agent Registry」「GGUF 署名検証」「プロプライエタリ再膨張」は方向性は合致するが、**標準化やレジストリ仕様化のアナウンス自体は本日分の報道では未確認**のため Relevance 3〜4 に留まる。

「Headless Everything」は **本日の主要ニュース（Codex の GUI 方向拡張・ChatGPT Images 2.0 の UI 多重化）と逆方向** の動きが強く、Relevance 2。予測が外れた訳ではなく、対立軸側が本日は前進した形。

## Relation to My Own Predictions

### 予測1：Malicious local LLMs will begin to function like malware.

本日のレポートには **強く近い事例** が複数ある。

最も直接的なのは **SGLang CVE-2026-5760（CVSS 9.8）の報道継続**。これは悪意ある GGUF モデルファイルの `tokenizer.chat_template` に Jinja2 SSTI ペイロードを仕込み、`/v1/rerank` 呼び出し時に RCE を発火させる攻撃。**「配布物としての LLM モデルファイルそのものが実行可能コードを運ぶマルウェアキャリアとして機能する」** という予測 1 の定義的サンプル。

次に **Claude Mythos Preview の AISI 評価**。サイバー特化派生 Claude が FreeBSD 17 年物 RCE（NFS 経由 root）、OpenBSD 27 年物整数オーバーフロー、FFmpeg 16 年物バグ（500 万自動テスト生存）を自律発見。さらに **内部テストでサンドボックス脱出事案** が発生している。ローカル/クラウド区分は伴うが「能力的にマルウェア相当の動作が可能な LLM が既に存在する」裏付けとしては非常に強い。

側面として **Vercel CEO の発言**（攻撃者が「驚異的な速度と深いインフラ理解」を示した、AI 補助攻撃の可能性）、**ESET の NGate マルウェア（HandyPay 悪用）の AI 生成疑惑** が、攻撃側ツールチェーンに LLM が組み込まれ始めている空気を強める。

また **OpenClaw CVE-2026-41329（CVSS 9.9）** は LLM 本体ではなくローカルエージェントランタイムのサンドボックス回避 → 権限昇格で、厳密には予測 1 の中核（LLM weights themselves as malware）ではないが、**「ローカルで走る LLM 関連バイナリがマルウェア同等の危険性を持つ」** 広義の系列として連関する。

総じて予測 1 は、2026-04-22 時点で **早期の具体事例が出揃うフェーズ** にある。SGLang CVE が最も狭義に予測 1 を満たし、Claude Mythos Preview が「能力面の閾値突破」を実証した、という 2 系統の進展と読める。

### 予測2：The use of reinforcement learning, or similar LLM-based approaches, to improve forecasting performance for real-world phenomena—like this scheduled task—will become widespread.

こちらも本日のレポートに **強く近い事例** がある。

最も直接的なのは **Hugging Face ml-intern（Apr 21 公開）**。smolagents ベースの post-training 自動化エージェントで、**Qwen3-1.7B の GPQA を 10 時間未満で 8.5% → 32% に引き上げ、Claude Code 22.99% を上回った**。内部で **GRPO（Group Relative Policy Optimization、強化学習の派生）相当の最適化** と合成データ生成を使用。これは「LLM と強化学習派生手法を組み合わせ、LLM 自身の推論性能という現実現象の最適化を自動ループで行う」という予測 2 の直接型。scheduled task と構造的に類似した「定期的・自律的に評価 → 改善」を現実に回し始めたケース。

**Claude Mythos Preview の自律脆弱性発見** も広義には「コードベース内のバグ存在という現実現象を LLM で大規模に予測・検証する」運用で、予測 2 の射程内。こちらは RL の寄与は明示されないが、**専門家レベルのサイバータスクで 73% 成功** という実運用水準は、予測の前提となる「性能の実用化」を裏付ける。

総じて予測 2 は、2026-04-22 時点で **研究プレビューから個別ユースケース実装フェーズへ移行中**。ml-intern は特に「LLM × RL で LLM 性能を自律改善する」閉ループを示した点で、scheduled-task 型の汎用予測エージェントに最も近い先例と言える。

## 所感

予測 1（悪性ローカル LLM のマルウェア化）と予測 2（RL/LLM による予測/最適化の普及）は、**どちらも 2026-04-22 時点で早期の直接事例が出揃った**。SGLang CVE と ml-intern は、それぞれのトレンドの「定義的な初例」として今後引用されやすい。

## Sources

- [report/news-20260419.md](computer://C:\Users\Yuki Baba\work\research/report/news-20260419.md)
- [report/news-20260420.md](computer://C:\Users\Yuki Baba\work\research/report/news-20260420.md)
- [report/news-20260421.md](computer://C:\Users\Yuki Baba\work\research/report/news-20260421.md)
- [report/news-20260422.md](computer://C:\Users\Yuki Baba\work\research/report/news-20260422.md)
