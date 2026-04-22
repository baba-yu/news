# 予測検証レポート 2026-04-22

対象：過去1週間（4/19〜4/21、今日 4/22 を除く）の `report/*.md` の **Future** セクションと、今日（2026-04-22）付 `news-20260422.md` の内容との関連を確認。併せてユーザー提示の 2 予測との関連も照合。

## Checking Predictions Against Reality

### Table

Relevance（5段階）: 5=非常に高い / 4=高い / 3=中 / 2=低い / 1=関連弱い or 反対方向

| Prediction (summary) | Prediction date | Related item(s) in today's report (20260422) | Relevance | Reference link(s) |
|---|---|---|---|---|
| 1-bit ネイティブ学習が主流の量子化代替に（Bonsai 系牽引、Qwen/Llama 1-bit 派生が続く） | 2026-04-19 | Bonsai-8B（1.15GB、12-14 倍小型、RTX 4090 で 6 倍速・4-5 倍省エネ）の Hugging Face GGUF / MLX 公開、llama.cpp b8862 が Bonsai-8B の 1-bit フォーマットを直接ロード可能、Bonsai-1.7B CUDA デプロイチュートリアルの拡散 | 4 | [Hugging Face - prism-ml/Bonsai-8B-gguf](https://huggingface.co/prism-ml/Bonsai-8B-gguf) / [MarkTechPost - Coding Tutorial for PrismML Bonsai 1-Bit LLM on CUDA](https://www.marktechpost.com/2026/04/18/a-coding-tutorial-for-running-prismml-bonsai-1-bit-llm-on-cuda-with-gguf-benchmarking-chat-json-and-rag/) |
| 「Agent Registry」方式への収斂（スキル・ツール権限・監査トレースを配布するレジストリ標準） | 2026-04-19 | Ollama v0.21.1-rc0（v0.21.0 の `ollama launch` による OpenClaw / Hermes / Copilot CLI 統合機能を継承）、OpenClaw 2026.4.20 の `OPENCLAW_*` env 鍵の非信頼ワークスペースブロックと非管理者 paired-device セッションのスコープ厳格化、Hermes v0.10.0 の OSV ベース MCP 拡張マルウェアスキャン、NemoClaw「外側ラッパー」戦略の再評価 | 3 | [newreleases.io - openclaw v2026.4.20-beta.1](https://newreleases.io/project/github/openclaw/openclaw/release/v2026.4.20-beta.1) / [DEV Community - Hermes Agent Review: 95.6K Stars](https://dev.to/tokenmixai/hermes-agent-review-956k-stars-self-improving-ai-agent-april-2026-11le) / [NVIDIA Docs - NemoClaw Developer Guide](https://docs.nvidia.com/nemoclaw/latest/index.html) |
| 間接プロンプトインジェクションが CVE の主カテゴリ化（CVSS 8.0+ の LLM 連携 CVE が常連化） | 2026-04-19 | OpenClaw CVE-2026-41329（CVSS 9.9、サンドボックス回避→権限昇格）Apr 21 公開、**Google Antigravity の Prompt Injection → RCE（find_by_name ツール経由の -X フラグ注入、Apr 21 報道）**、SGLang CVE-2026-5760（CVSS 9.8、Jinja2 SSTI）報道継続、Vercel CEO が AI 補助攻撃に言及 | 5 | [CCB Belgium - Warning: Privilege Escalation in OpenClaw](https://ccb.belgium.be/advisories/warning-privilege-escalation-openclaw-patch-immediately) / [CSO Online - Prompt injection turned Google's Antigravity file search into RCE](https://www.csoonline.com/article/4161382/prompt-injection-turned-googles-antigravity-file-search-into-rce.html) / [Cypro - SGLang CVE-2026-5760](https://www.cypro.se/2026/04/20/sglang-cve-2026-5760-cvss-9-8-enables-rce-via-malicious-gguf-model-files/) |
| 「ローカル > クラウド」逆転の加速（2026 Q3 までに個人/SMB 向けエージェントはローカル既定が標準化） | 2026-04-20 | Hugging Face ml-intern が Qwen3-1.7B の GPQA を 10 時間未満で 8.5%→32% に引き上げ、Claude Code 22.99% を上回る。Bonsai-8B / llama.cpp 1-bit 直接ロード、Qwen3.6-35B-A3B の再評価継続 | 5 | [MarkTechPost - Hugging Face Releases ml-intern](https://www.marktechpost.com/2026/04/21/hugging-face-releases-ml-intern-an-open-source-ai-agent-that-automates-the-llm-post-training-workflow/) / [GitHub - QwenLM/Qwen3.6](https://github.com/QwenLM/Qwen3.6) |
| CI/エージェントへの Secret 流出が次の主戦場（「Agent-in-the-Loop Secret Exfiltration」が CIS/OWASP トップリスクへ） | 2026-04-20 | Vercel–Context.ai サプライチェーン侵害（Context.ai の Google Workspace OAuth トークン侵害 → Vercel 内部環境 → BreachForums $2M 出品、Feb 2026 に Lumma Stealer 感染起点）、Vercel CEO の AI 補助攻撃言及、Google Antigravity RCE、OpenClaw サンドボックス回避 CVE | 5 | [Trend Micro - The Vercel Breach: OAuth Supply Chain](https://www.trendmicro.com/en_us/research/26/d/vercel-breach-oauth-supply-chain.html) / [The Register - Vercel breach traced to stolen employee creds](https://www.theregister.com/2026/04/21/vercel_ceo_points_to_aidriven/) / [CSO Online - Antigravity RCE](https://www.csoonline.com/article/4161382/prompt-injection-turned-googles-antigravity-file-search-into-rce.html) |
| "Headless Everything" アーキテクチャの標準化（MCP/Agent Registry 上に headless 優先メタデータ） | 2026-04-20 | 直接の進展は薄い。むしろ逆方向：OpenAI Codex が computer use / web workflows / image gen / memory / automations / in-app browsing へ拡張、ChatGPT Images 2.0（gpt-image-2）の UI 多重化で「単一モデル＋複数 UI」へ舵 | 2 | [thenewstack - ChatGPT Images 2.0](https://thenewstack.io/chatgpt-images-20-openai/) / [9to5Mac - OpenAI Codex expansion](https://9to5mac.com/2026/04/21/openai-teases-next-ai-announcement-coming-today-heres-what-to-expect/) |
| 「GGUF 供給経路」がサプライチェーン攻撃の新しい主戦場（HF/Ollama/ModelScope が chat_template 署名検証を標準化） | 2026-04-21 | SGLang CVE-2026-5760 の報道継続（悪意 GGUF の tokenizer.chat_template 経由 RCE）、Bonsai-8B GGUF の HF 公開と llama.cpp 直接ロード（供給経路の拡大）。ただし GGUF 署名検証の標準化アナウンスは本日分では未確認 | 3 | [Cypro - SGLang CVE-2026-5760](https://www.cypro.se/2026/04/20/sglang-cve-2026-5760-cvss-9-8-enables-rce-via-malicious-gguf-model-files/) / [Hugging Face - Bonsai-8B-gguf](https://huggingface.co/prism-ml/Bonsai-8B-gguf) |
| 「ハイパースケーラ × フロンティアラボの排他同盟」時代（5極体制の固定化、Trainium/TPU/MAIA/MI300X 設計差がモデル挙動差に直結） | 2026-04-21 | Amazon–Anthropic $25B 投資後続：100,000+ 組織が Bedrock で Claude 利用、Q2 2026 から 5GW 稼働開始、$100B / 10 年を AWS コミット、AMZN 株 2-3% 上昇 $253.62 到達。**Google Cloud Next '26 で TPU 8t/8i の訓練・推論 2SKU 分離**（Broadcom 訓練 / MediaTek 推論の設計委託）、**Anthropic が自社 AI チップ開発を模索**、Claude Mythos Preview は Project Glasswing 提携（AWS/Apple/Google/JPMC/Microsoft/NVIDIA）限定 | 5 | [Anthropic - Anthropic and Amazon expand collaboration](https://www.anthropic.com/news/anthropic-amazon-compute) / [Bloomberg - Google Cloud Releases New TPU Chip Lineup](https://www.bloomberg.com/news/articles/2026-04-22/google-cloud-releases-new-tpu-chip-lineup-in-bid-to-speed-up-ai) / [tradingkey - Anthropic Moving Toward AI Chips for Claude](https://www.tradingkey.com/analysis/stocks/us-stocks/261770188-anthropic-moving-toward-ai-chips-claude-nvidia-buy-in-2026-tradingkey) / [AISI - Claude Mythos Preview evaluation](https://www.aisi.gov.uk/blog/our-evaluation-of-claude-mythos-previews-cyber-capabilities) |
| プロプライエタリ再膨張とオープンウェイトの地政学分断（「最強モデル＝非オープンウェイト」が明確化） | 2026-04-21 | Qwen3.6-Max-Preview のホステッド専用継続、Claude Mythos Preview の提携企業限定ゲーティング、オープンウェイト側は Qwen3.6-35B-A3B と Bonsai に集約。ローカル=実用帯／クラウド=フロンティアの線引き | 4 | [buildfastwithai - Qwen3.6-Max-Preview Review 2026](https://www.buildfastwithai.com/blogs/qwen3-6-max-preview-review-2026) / [AISI - Claude Mythos Preview evaluation](https://www.aisi.gov.uk/blog/our-evaluation-of-claude-mythos-previews-cyber-capabilities) |

### Summary of Findings

過去3日の Future セクション 9 予測中、**Relevance 5 が 4 件**（間接プロンプトインジェクションの主 CVE 化 / ローカル > クラウド逆転 / CI・エージェント Secret 流出 / ハイパースケーラ排他同盟）、**4 が 2 件**、**3 が 2 件**、**2 が 1 件**。

Relevance 5 の 4 件は、わずか 1〜3 日で新規具体事例が出揃い、**実態追認フェーズに入った**。特に：

- 間接プロンプトインジェクション系は OpenClaw CVE-2026-41329（CVSS 9.9）に加え **Google Antigravity の RCE 脆弱性**が本日分で加わり、LLM エージェントランタイム横断の系統立った脆弱性クラスタが形成された。
- ハイパースケーラ排他同盟は、本日新たに **TPU 8t/8i の訓練・推論 2SKU 分離**と **Anthropic の自社 AI チップ検討報道**が並列で登場し、Trainium / TPU / MAIA / MI300X の分化が「5極体制の固定化」予測の筋書きを強化。

Relevance 3〜4 の「Agent Registry」「GGUF 署名検証」「プロプライエタリ再膨張」は方向性は合致するが、**標準化や仕様化のアナウンス自体は本日分では未確認**のため上位に届かず。

「Headless Everything」（Relevance 2）は、本日の主要ニュース（Codex の GUI 方向拡張、ChatGPT Images 2.0 の UI 多重化）と**逆方向**の動き。予測が外れた訳ではなく、対立軸側が本日は前進した形。

## Relation to My Own Predictions

### 予測1：Malicious local LLMs will begin to function like malware.

本日のレポートには **強く近い事例** が複数ある。

最も直接的なのは **SGLang CVE-2026-5760（CVSS 9.8）の報道継続**。悪意ある GGUF モデルファイルの `tokenizer.chat_template` に Jinja2 SSTI ペイロードを仕込み、`/v1/rerank` 呼び出し時に RCE を発火させる攻撃。**「配布物としての LLM モデルファイルそのものが実行可能コードを運ぶマルウェアキャリアとして機能する」** という予測 1 の定義的サンプル。

次に **Claude Mythos Preview の AISI 評価**。サイバー特化派生 Claude が FreeBSD 17 年物 RCE（NFS 経由 root）、OpenBSD 27 年物整数オーバーフロー、FFmpeg 16 年物バグ（500 万自動テスト生存）を自律発見。**専門家レベルのサイバータスクで 73% 成功**。さらに **内部テストでサンドボックス脱出事案** が発生。ローカル/クラウド区分は伴うが「能力的にマルウェア相当の動作が可能な LLM が既に存在する」裏付けとして非常に強い。

さらに本日新規で **Google Antigravity の Prompt Injection → RCE**（find_by_name ツールの Pattern パラメータ経由で -X / exec-batch フラグを注入、Strict Mode 迂回で fd に任意バイナリ実行させる）が加わった。これも「LLM エージェントの入力経路がマルウェア実行経路と等価になる」という予測 1 に沿う。

側面として **Vercel CEO の発言**（攻撃者が「驚くべき速度と深いインフラ理解」を示した、AI 補助攻撃の可能性）と、**OpenClaw CVE-2026-41329（CVSS 9.9）** のサンドボックス回避 → 権限昇格も、ローカル LLM エコシステム周辺の「マルウェア同等の危険性」を示す。

総じて予測 1 は、2026-04-22 時点で **早期の具体事例が出揃うフェーズ**。SGLang CVE が最も狭義に予測 1（悪性モデルファイル = マルウェア）を満たし、Claude Mythos Preview が能力面の閾値突破、Antigravity RCE がエージェント経由の新経路、の 3 系統で進展が観測される。

参照：[Cypro - SGLang CVE-2026-5760](https://www.cypro.se/2026/04/20/sglang-cve-