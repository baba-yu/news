# 予測検証レポート 2026-04-23

<!-- ai-notice -->
> **ご注意:** 本ページの記事および要約は、Anthropic 社の生成AI「Claude」によって作成されています。


対象：過去1週間（4/19〜4/22、今日 4/23 を除く）の `report/*.md` の **Future** セクションと、今日（2026-04-23）付 `news-20260423.md` の内容との関連を確認。併せてユーザー提示の 2 予測との関連も照合。

## Checking Predictions Against Reality

### Table

Relevance（5段階）: 5=非常に高い / 4=高い / 3=中 / 2=低い / 1=関連弱い or 反対方向

| Prediction (summary) | Prediction date | Related item(s) in today's report (20260423) | Relevance | Reference link(s) |
|---|---|---|---|---|
| 1-bit ネイティブ学習が主流の量子化代替に（Bonsai 系牽引、Qwen/Llama 1-bit 派生が続く） | 2026-04-19 | Bonsai-8B の解説／デプロイ記事が継続拡散（Medium / getdeploying / Firethering）。ただし Qwen / Llama の 1-bit 派生は本日分では新規登場せず、むしろ Qwen3.6-27B **Dense BF16/FP8** が「実質ローカルフラグシップ」のポジションを取った | 2 | [Medium - New 1 bit LLM is here: Bonsai-8B](https://medium.com/data-science-in-your-pocket/new-1-bit-llm-is-here-bonsai-8b-bc6074403e50) / [getdeploying - Bonsai 1-bit](https://getdeploying.com/guides/bonsai-1bit-llm) / [Firethering - Bonsai 8B](https://firethering.com/bonsai-8b-1bit-llm/) |
| 「Agent Registry」方式への収斂（スキル・ツール権限・監査トレースを配布するレジストリ標準） | 2026-04-19 | **Google Gemini Enterprise Agent Platform**（Agent Designer / Inbox / Skills / Projects / Model Garden 200+ モデル / マネージド MCP サーバ / A2A 本番版）、**AWS Bedrock AgentCore Managed Harness + CLI + プリビルド skills**（Kiro / Claude Code / Codex / Cursor 向け）、**OpenAI Workspace Agents**（Codex 駆動、組織パーミッション内常駐）が同日に並列発表。スキル／ツール権限／監査を単一面で提供する構図が固まった | 5 | [Google Cloud - Introducing Gemini Enterprise Agent Platform](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) / [AWS - Amazon Bedrock AgentCore adds new features](https://aws.amazon.com/about-aws/whats-new/2026/04/agentcore-new-features-to-build-agents-faster/) / [OpenAI - Introducing workspace agents in ChatGPT](https://openai.com/index/introducing-workspace-agents-in-chatgpt/) |
| 間接プロンプトインジェクションが CVE の主カテゴリ化（CVSS 8.0+ の LLM 連携 CVE が常連化） | 2026-04-19 | 本日公開の重大 CVE 群（Xerte 9.8 / Esri 9.8 / Web App PrivEsc 9.6 / Nimiq 9.6 / Jellystat 9.1 / OAuth2 Proxy 9.1 / EspoCRM 9.1 / Microsoft Defender KEV）は従来型 Web / OAuth / SSTI 系中心で、**LLM 連携直系の新規 CVE は本日分では未確認**。ただし Google Cloud の新ガバナンス説明で「indirect prompt injection / 過剰共有 / データ漏洩リスクを低減」と明示され、設計面では主カテゴリ化が進展 | 3 | [Google Cloud - The new Gemini Enterprise](https://cloud.google.com/blog/products/ai-machine-learning/the-new-gemini-enterprise-one-platform-for-agent-development) / [TheHackerWire - Xerte Online Toolkits RCE](https://www.thehackerwire.com/xerte-online-toolkits-rce-via-incomplete-input-validation-cve-2026-34415/) |
| 「ローカル > クラウド」逆転の加速（2026 Q3 までに個人/SMB 向けエージェントはローカル既定が標準化） | 2026-04-20 | **Qwen3.6-27B Dense（Apache 2.0）が SWE-bench Verified 77.2% で Qwen3.5-397B-A17B MoE を上回り Claude Opus 4.5/4.6 同等**、GGUF Q4_K_M で VRAM 約 18GB、**RTX 4090 1 枚でフラグシップ級コーディング**。Simon Willison が「27B Dense でフラグシップ級」と評価、GIGAZINE が「Claude Opus 4.5 近似をローカル PC で」と報道 | 5 | [MarkTechPost - Qwen3.6-27B](https://www.marktechpost.com/2026/04/22/alibaba-qwen-team-releases-qwen3-6-27b-a-dense-open-weight-model-outperforming-397b-moe-on-agentic-coding-benchmarks/) / [byteiota - Qwen3.6-27B on RTX 4090](https://byteiota.com/qwen3-6-27b-flagship-coding-on-rtx-4090-local/) / [Simon Willison - Qwen3.6-27B](https://simonwillison.net/2026/Apr/22/qwen36-27b/) / [GIGAZINE - Qwen3.6-27B](https://gigazine.net/gsc_news/en/20260423-qwen-3-6-27b/) |
| CI/エージェントへの Secret 流出が次の主戦場（「Agent-in-the-Loop Secret Exfiltration」が CIS/OWASP トップリスクへ） | 2026-04-20 | **Anthropic Claude Mythos Preview の未認可アクセス事案**：第三者ベンダ環境で外注スタッフのクレデンシャル + Mercor 流出データ + 命名規則推測で Private Discord グループがエンドポイントに到達。**OAuth2 Proxy CVE-2026-40575（9.1、X-Forwarded-Uri で認証バイパス）** も同期して公開 | 4 |  / [CyberNews - Discord group accessed Mythos](https://cybernews.com/security/anthropic-mythos-ai-unauthorized-access/) / [TheHackerWire - OAuth2 Proxy CVE-2026-40575](https://www.thehackerwire.com/oauth2-proxy-x-forwarded-uri-authentication-bypass-cve-2026-40575/) |
| "Headless Everything" アーキテクチャの標準化（MCP/Agent Registry 上に headless 優先メタデータ） | 2026-04-20 | 本日分は **逆方向** の動きが強い。**Google Project Mariner（web-browsing agent）**、**Workspace Studio no-code agent builder**、**OpenAI Workspace Agents の Slack / Salesforce 直接統合**など、GUI / ブラウザ側の自動化が前進。headless 優先メタデータの標準化アナウンスは本日分では未確認 | 2 | [TheNextWeb - Google Cloud Next 2026: AI agents, A2A, Workspace Studio](https://thenextweb.com/news/google-cloud-next-ai-agents-agentic-era) / [SiliconANGLE - OpenAI workspace agents](https://siliconangle.com/2026/04/22/openai-subscribers-get-new-workspace-agents-automate-complex-tasks-across-teams/) |
| 「GGUF 供給経路」がサプライチェーン攻撃の新しい主戦場（HF/Ollama/ModelScope が chat_template 署名検証を標準化） | 2026-04-21 | **Qwen3.6-27B の BF16 / FP8 版が Hugging Face Hub / ModelScope に同時公開**、**GGUF Q4_K_M で llama.cpp 直接ロード**など供給経路は拡大。ただし chat_template 署名検証／GGUF SSTI スキャンの標準化アナウンスは本日分では未確認。SGLang CVE-2026-5760 関連の新続報もなし | 2 | [MarkTechPost - Qwen3.6-27B](https://www.marktechpost.com/2026/04/22/alibaba-qwen-team-releases-qwen3-6-27b-a-dense-open-weight-model-outperforming-397b-moe-on-agentic-coding-benchmarks/) / [byteiota - Qwen3.6-27B RTX 4090](https://byteiota.com/qwen3-6-27b-flagship-coding-on-rtx-4090-local/) |
| 「ハイパースケーラ × フロンティアラボの排他同盟」時代（5極体制の固定化、Trainium/TPU/MAIA/MI300X 設計差がモデル挙動差に直結） | 2026-04-21 | **Anthropic + Google + Broadcom：2027 開始の複数 GW 級 TPU 追加契約**、Mizuho 試算で Broadcom が Anthropic から 2026 $21B / 2027 $42B 収益獲得。**Anthropic 年率売上 $30B 超**で OpenAI $25B を上回る。**NVIDIA Vera Rubin 7 チップ量産入り**（AWS / Google Cloud / Azure / OCI / CoreWeave / Lambda / Nebius / Nscale が順次 Vera Rubin インスタンス提供）。Google Cloud Next '26 の Model Garden に Claude を含む 200+ モデル配備 | 5 |  / [The Motley Fool - Anthropic Announcement for Alphabet and Broadcom](https://www.fool.com/investing/2026/04/22/anthropic-just-announced-huge-news-for-alphabet-an/) / [NVIDIA Newsroom - NVIDIA Vera Rubin Platform](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform) /  |
| プロプライエタリ再膨張とオープンウェイトの地政学分断（「最強モデル＝非オープンウェイト」が明確化） | 2026-04-21 | **Gemini 3.1 Pro / Gemini 3.1 Flash Image / Lyria 3 は Google Cloud ホステッド独占**、Claude Mythos Preview は第三者ベンダ境界にゲーティング。一方で **Qwen3.6-27B Apache 2.0 がコーディング SWE-bench で MoE 397B を超えフラグシップ級** に到達、オープンウェイト側が逆流を示す。線引きは「フロンティア=ホステッド / 実用帯=オープン」で維持されるが、27B Dense がコーディング特化タスクでフロンティア境界を侵食 | 3 | [Google Cloud - Introducing Gemini Enterprise Agent Platform](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform) / [buildfastwithai - Qwen3.6-27B review](https://www.buildfastwithai.com/blogs/qwen3-6-27b-review-2026) /  |
| 「訓練 / 推論の SKU 分離」がカスタム AI シリコンの標準設計に | 2026-04-22 | **NVIDIA Vera Rubin プラットフォーム 7 チップ量産入り**（Vera CPU / Rubin GPU / NVLink 6 Switch / ConnectX-9 / BlueField-4 / Spectrum-6 / Groq 3 LPU）は **単一アーキスタックの統合強化**で、予測と逆方向。一方 **Anthropic が Google TPU（Broadcom 経由）で 2027 GW 級追加契約**はハイパースケーラ側の推論最適化 SKU 増産を継続的に示す | 3 | [NVIDIA Newsroom - Vera Rubin Platform](https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform) /  |
| Physical AI の SaaS 化と「Robot-as-a-Service」基盤競争（ロボット本体はコモディティ、フリート管理ソフトが経常収益化） | 2026-04-22 | **Hannover Messe 2026 で Agile Robots「ブルーアイ」工具箱詰め実演**、**Accenture + Vodafone Procure & Connect + SAP のヒューマノイド倉庫業務パイロット**、**Tesla Optimus V3（37 関節 / 1.2m/s）Fremont 7-8月生産開始、Giga Texas 第2工場 2027 夏稼働、最終 10M 台目標**、**ヒューマノイド市場 2026 $2.16B→2035 $8.78B 試算**、**Woven by Toyota が Woven City 全域に自社 AI「カケザン」展開**。実装・パイロット・市場化が同時並列で進展 | 5 | [BSS News - Agile Robots / German factories](https://www.bssnews.net/news/380249) / [Robotics Tomorrow - Accenture Vodafone SAP Humanoid Warehouse](https://www.roboticstomorrow.com/news/2026/04/22/accenture-vodafone-procure-connect-and-sap-pilot-humanoid-robotics-in-warehouse-operations/26460/) / [The Robot Report - Tesla 10M Optimus](https://www.therobotreport.com/from-evs-to-robotics-tesla-targets-10m-optimus-units-with-new-texas-plant/) / [GlobeNewswire - Humanoid Robot Market $8.78B by 2035](https://www.globenewswire.com/news-release/2026/04/22/3278870/0/en/Humanoid-Robot-Market-Size-Worth-USD-8-78-Billion-by-2035-Driven-by-AI-Advancements-and-Expanding-Industrial-and-Consumer-Applications.html) / [Toyota Global - Woven City Kakezan](https://global.toyota/en/newsroom/corporate/44256155.html) |
| AI SaaS 間の OAuth 横断信任が最大のエンタープライズリスクに | 2026-04-22 | **Anthropic Mythos Preview 未認可アクセスは第三者ベンダ境界＋クレデンシャル悪用＋命名規則推測**の組み合わせで、前日の Vercel–Context.ai OAuth サプライチェーン侵害と同型の構造をフロンティアモデル側で再演。**OAuth2 Proxy CVE-2026-40575（X-Forwarded-Uri で認証バイパス）** が同日公開、Google Cloud の AI Control Center / Agent Management がガバナンス機能として指名 | 4 |  /  / [TheHackerWire - OAuth2 Proxy CVE-2026-40575](https://www.thehackerwire.com/oauth2-proxy-x-forwarded-uri-authentication-bypass-cve-2026-40575/) / [Google Workspace - 10 more announcements at Next 2026](https://workspace.google.com/blog/product-announcements/10-more-announcements-workspace-at-next-2026) |

### Summary of Findings

過去4日の Future セクション 12 予測中、**Relevance 5 が 4 件**（Agent Registry / ローカル > クラウド逆転 / ハイパースケーラ排他同盟 / Physical AI SaaS 化）、**4 が 2 件**、**3 が 3 件**、**2 が 3 件**。

Relevance 5 の 4 件は、本日の主要発表（Google Cloud Next '26 / Qwen3.6-27B / Anthropic TPU 拡張 / Hannover Messe + Tesla Optimus）と**ほぼ 1:1 で対応**する形で実態追認が進んだ。特に：

- 「Agent Registry」予測は **Google Gemini Enterprise Agent Platform / AWS Bedrock AgentCore Managed Harness / OpenAI Workspace Agents** が同日に並列発表される形で、ハイパースケーラ 3 社が揃って「エージェントのライフサイクル単一面」を持つ構図が本日確定した。
- 「ローカル > クラウド逆転」予測は **Qwen3.6-27B Dense（Apache 2.0、RTX 4090 1 枚でフラグシップ級）** の登場で、MoE 複雑性を回避した Dense で SWE-bench 77.2% を達成、「ローカル = 実用帯」の上限がフロンティア級に食い込んだ点でも強化。
- 「ハイパースケーラ排他同盟」予測は **Anthropic TPU / Broadcom 追加契約 + 年率 $30B 売上 + Vera Rubin 7 チップ量産** が並列で登場。
- 「Physical AI SaaS 化」予測は **Hannover Messe 実演 + Accenture パイロット + Tesla Optimus 生産確定 + Woven City** の 4 軸が同時進展、実装フェーズに移行した。

Relevance 3〜4 の「CI/エージェント Secret 流出」「プロプライエタリ再膨張」「訓練/推論 SKU 分離」「OAuth 横断信任リスク」「間接プロンプトインジェクション CVE 主カテゴリ化」は方向性は合致するが、**単一の決定的イベントよりは複合的進展** であり、標準化アナウンス自体は本日分では未確認。

Relevance 2 の「1-bit ネイティブ学習」「Headless Everything」「GGUF 署名検証」は、本日分では**逆方向または進展薄**。特に「1-bit」は Qwen3.6-27B Dense が**1-bit ではなく BF16/FP8 Dense で勝った**点が、予測経路とは別解の成立を示唆。「Headless Everything」は Google Project Mariner / Workspace Studio / Slack・Salesforce 統合など GUI 側の自動化が前進する**反対方向**の動き。

## Relation to My Own Predictions

### 予測1：Malicious local LLMs will begin to function like malware.

本日のレポートは、**予測 1 の直接的な新規事例は薄い**。前回（2026-04-22）で SGLang CVE-2026-5760（悪意 GGUF の Jinja2 SSTI → RCE）と Google Antigravity Prompt Injection → RCE が最も狭義のサンプルとして捕捉されたが、今日分では SGLang CVE の続報・Antigravity 関連の新情報は無く、AI フレームワーク直系の新規重大 CVE も出ていない。

ただし**間接的に関連する事案**が複数ある。

最も重要なのは **Anthropic Claude Mythos Preview の未認可アクセス事案**。Mythos は AISI 評価で専門家レベルのサイバータスク 73% 成功・内部テストでサンドボックス脱出を起こした「公開するには危険すぎる」能力モデルであり、**公開初日に Private Discord グループが到達**した。彼らの主張では「シンプルな Web サイト構築」止まりでマルウェア使用は無いが、**「マルウェア同等能力の LLM にアクセス可能な非認可主体が存在する」という前提条件**が既に成立していることを示す点で、予測 1 の直接前段階事例。Euronews が「公開するには危険すぎる Mythos AI モデルをハッカーが侵害」と見出しを付けた通り、**マルウェア化直前の能力閾値 × アクセス制御破綻**の両立を記録した日。

次に **OAuth2 Proxy CVE-2026-40575（9.1、X-Forwarded-Uri 経由認証バイパス）** と **Microsoft Defender CVE-2026-33825 の CISA KEV 追加**（アクセス制御粒度不足でポリシ迂回）も、「LLM エージェントがこれらのインフラに触れる際、セキュリティ境界の代替執行者として動作する」文脈で予測 1 の運用側面に絡む。

**OpenClaw v2026.4.21** が前回の CVE-2026-41329（CVSS 9.9、サンドボックス回避→権限昇格）を塞いだ「セキュリティ固定」リリースである点も、**LLM エージェントランタイム自体が権限昇格マルウェア経路と等価になる**という予測 1 の裏面を反映している。

総じて予測 1 は、2026-04-23 時点で **「能力の閾値突破」「アクセス制御破綻」「ランタイム権限の修復」** の 3 系統で水面下の進展が続き、次の「明確なマルウェア動作事例」が出るための部品は揃っている状況。

参照： / [Euronews - Hackers breach Anthropic's 'too dangerous to release' Mythos](https://www.euronews.com/next/2026/04/22/hackers-breach-anthropics-too-dangerous-to-release-mythos-ai-model-report) / [TheHackerWire - OAuth2 Proxy CVE-2026-40575](https://www.thehackerwire.com/oauth2-proxy-x-forwarded-uri-authentication-bypass-cve-2026-40575/) / [CISA - Microsoft Defender KEV addition](https://www.cisa.gov/news-events/alerts/2026/04/22/cisa-adds-one-known-exploited-vulnerability-catalog) / [Efficient Coder - OpenClaw v2026.4.21 Release](https://www.xugj520.cn/en/archives/openclaw-2026-4-21-release-updates.html)

### 予測2：The use of reinforcement learning, or similar LLM-based approaches, to improve forecasting performance for real-world phenomena—like this scheduled task—will become widespread.

本日のレポートに**直接の強い対応事例は薄い**。前回（2026-04-22）の Hugging Face ml-intern（GRPO 相当で Qwen3-1.7B GPQA を 8.5% → 32% に自動改善）ほど「LLM × RL で LLM 性能を自律改善する閉ループ」の決定的事例は出ていない。

ただし**予測の射程に入る動き**が複数ある。

最も近いのは **OpenAI Workspace Agents**。Codex 駆動で **組織のパーミッション内でクラウド常駐**、ファイル／コード／ツール／Slack／Salesforce 横断で**「定期的・自律的にタスクを実行する」例として Weekly Metrics Reporter / Product Feedback Router / Software Reviewer** が公式例示された。これは scheduled-task 型の汎用予測・ルーチン実行エージェントと**構造的に同型**。RL の明示的寄与は不明だが、**「LLM エージェントが現実世界の定期観測ループを回す」汎用プラットフォーム** の登場という意味で、予測 2 の基盤側進展。

**Microsoft Foundry Fine-Tuning 強化**（RFT = Reinforcement Fine-Tuning を o4-mini / GPT-4.1 にグローバル展開、RFT ベストプラクティスガイド公開）も予測 2 に直接該当する。RFT は LLM 向け強化学習手法の商用化名であり、**「フロンティアモデルの性能を現実世界のタスク定義で継続的に最適化する」枠組みが主要プラットフォームの標準メニュー化**しつつある点で、予測 2 の本筋。

**Qwen3.6-27B の Thinking Preservation 機構**（思考と応答を分離し、推論の長鎖を温存した上で応答品質を高める）も、Dense アーキ側からの「LLM の推論過程を現実タスクに合わせて最適化する」方向性で予測 2 の周辺。

総じて予測 2 は、2026-04-23 時点で **基盤プラットフォーム（OpenAI Workspace Agents / Microsoft Foundry RFT / Google Agent Designer）の同時整備期** に入っており、ml-intern のような決定的なユースケース事例は本日分では出ていないが、「LLM × RL / 継続最適化による現実タスク性能改善」の**供給側のインフラが 3 社並列で揃った**。

参照：[OpenAI - Introducing workspace agents in ChatGPT](https://openai.com/index/introducing-workspace-agents-in-chatgpt/) / [Microsoft Learn - Foundry What's new for April 2026 (RFT)](https://learn.microsoft.com/en-us/azure/foundry/whats-new-foundry) / [Microsoft TechCommunity - Foundry Labs April 2026](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/whats-new-in-foundry-labs---april-2026/4509714) / [MarkTechPost - Qwen3.6-27B (Thinking Preservation)](https://www.marktechpost.com/2026/04/22/alibaba-qwen-team-releases-qwen3-6-27b-a-dense-open-weight-model-outperforming-397b-moe-on-agentic-coding-benchmarks/)

## 所感

本日（2026-04-23）は**「Agent Control Plane 3 社並列発表」「Qwen3.6-27B Dense の出現」「Anthropic TPU/Broadcom 拡張」「Physical AI パイロット同時進展」**の 4 ニュースで、過去 4 日の Future 予測のうち 4 件が同時に Relevance 5 を記録した**極めて密度の高い追認日**。特に「Agent Registry」「ローカル > クラウド」「排他同盟」「Physical AI SaaS 化」の 4 予測は、**単日で筋書きの大部分が実現**し、今後は「質の深化」フェーズに入る。

ユーザー予測 1（悪性ローカル LLM のマルウェア化）は本日分では直接事例は薄いが、Mythos の「危険モデル × アクセス制御破綻」が準備段階を完成。ユーザー予測 2（RL/LLM による予測/最適化の普及）は ml-intern のような決定的事例は出ていないが、OpenAI Workspace Agents / Microsoft Foundry RFT グローバル展開により**供給側のプラットフォーム整備が 3 社並列で完了**した日。

一方、「1-bit ネイティブ学習」「Headless Everything」「GGUF 署名検証」の 3 予測は、本日の Qwen3.6-27B Dense 登場 / GUI 自動化強化 / 署名検証未アナウンスにより**進展停滞または反対方向**。特に Qwen3.6-27B Dense が 1-bit ルートより先に「ローカル実用域でフロンティア迫る」を達成した点は、「1-bit ネイティブが唯一の量子化代替」という予測の前提が