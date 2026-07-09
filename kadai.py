import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import json
import os

# ページの設定
st.set_page_config(page_title="E-Lingo (英語学習継続アプリ)", page_icon="🦉", layout="wide")

# アカウントデータを保存するファイル名
USER_DB_FILE = "users.json"

# --- アカウントデータの読み込み・保存関数 ---
def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"user1": "password123"}  # 初期データ

def save_users(users):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# アカウントデータの初期化
if 'user_db' not in st.session_state:
    st.session_state.user_db = load_users()

# --- クイズのデータ（3大問 × 10問 ＝ 計30問） ---
QUIZ_CATEGORIES = {
    "🔥 1. 基礎英単語（中学〜高校レベル）": [
        {"question": "「〜に影響を与える」", "choices": ["Effect", "Affect", "Accept", "Effort"], "answer": "Affect", "hint": "Aから始まる動詞です"},
        {"question": "「〜を描写する、説明する」", "choices": ["Describe", "Destroy", "Decide", "Deliver"], "answer": "Describe", "hint": "デッサン（dessin）と似た語源です"},
        {"question": "「〜を保証する」", "choices": ["Gather", "Generate", "Guarantee", "Govern"], "answer": "Guarantee", "hint": "ギャランティー、保証書のことです"},
        {"question": "「〜を特定する、確認する」", "choices": ["Identify", "Ignore", "Illustrate", "Imply"], "answer": "Identify", "hint": "IDカードのIDはこの単語（Identity）からきています"},
        {"question": "「〜を避ける」", "choices": ["Avoid", "Admit", "Adapt", "Adopt"], "answer": "Avoid", "hint": "アボイド。危険などを避けるときに使います"},
        {"question": "「〜を期待する、予想する」", "choices": ["Expect", "Explain", "Express", "Explore"], "answer": "Expect", "hint": "Ex（外を）＋spect（見る）が語源です"},
        {"question": "「〜を改善する」", "choices": ["Improve", "Increase", "Include", "Ignore"], "answer": "Improve", "hint": "インプルーブ。スキルアップに欠かせない言葉です"},
        {"question": "「〜を提供する」", "choices": ["Provide", "Protect", "Prevent", "Promise"], "answer": "Provide", "hint": "プロバイダー（供給者）の動詞形です"},
        {"question": "「〜を受け入れる」", "choices": ["Accept", "Achieve", "Accuse", "Acquire"], "answer": "Accept", "hint": "アクセプト。提案などを快諾することです"},
        {"question": "「〜を思い出す」", "choices": ["Remember", "Remind", "Remove", "Repeat"], "answer": "Remember", "hint": "リメンバー。記憶に留めるという意味です"}
    ],
    "🚀 2. 応用英単語（大学受験〜TOEICレベル）": [
        {"question": "「代替の、代わりの」", "choices": ["Alternative", "Attention", "Approve", "Abuse"], "answer": "Alternative", "hint": "オルタナティブ・ロックなどの語源です"},
        {"question": "「一貫して、常に」", "choices": ["Constantly", "Consistently", "Conveniently", "Considerably"], "answer": "Consistently", "hint": "ブレずにずっと、という意味です"},
        {"question": "「重大な、批判的な」", "choices": ["Creative", "Critical", "Casual", "Certain"], "answer": "Critical", "hint": "ゲームの「クリティカルヒット」のクリティカルです"},
        {"question": "「〜を評価する」", "choices": ["Evaluate", "Encourage", "Establish", "Exaggerate"], "answer": "Evaluate", "hint": "バリュー（Value：価値）を外に引き出すという意味です"},
        {"question": "「〜を解釈する、通訳する」", "choices": ["Interrupt", "Interpret", "Introduce", "Invest"], "answer": "Interpret", "hint": "インタープリター（通訳者）の動詞形です"},
        {"question": "「重要な、かなりの」", "choices": ["Significant", "Sufficient", "Specific", "Simultaneous"], "answer": "Significant", "hint": "サイン（Sign）になるほどハッキリした、という意味です"},
        {"question": "「〜を維持する」", "choices": ["Maintain", "Manage", "Manufacture", "Measure"], "answer": "Maintain", "hint": "メンテナンス（Maintenance）の動詞形です"},
        {"question": "「〜を正確に推測する、見積もる」", "choices": ["Estimate", "Establish", "Eliminate", "Emphasize"], "answer": "Estimate", "hint": "エスティメイト。概算を出すときによく使います"},
        {"question": "「洗練された、精巧な」", "choices": ["Sophisticated", "Spontaneous", "Superficial", "Subsequent"], "answer": "Sophisticated", "hint": "都会的で垢抜けた、という意味も含みます"},
        {"question": "「〜を減少させる、減らす」", "choices": ["Diminish", "Distribute", "Disappear", "Display"], "answer": "Diminish", "hint": "だんだんと小さく、少なくなっていくイメージです"}
    ],
    "💼 3. ビジネス英単語（実践・仕事レベル）": [
        {"question": "「（締め切りなど）を延期する」", "choices": ["Postpone", "Predict", "Purchase", "Publish"], "answer": "Postpone", "hint": "Put off と同じ意味のフォーマルな動詞です"},
        {"question": "「〜を交渉する」", "choices": ["Negotiate", "Notify", "Nominate", "Navigate"], "answer": "Negotiate", "hint": "ネゴシエーション（交渉）の動詞形です"},
        {"question": "「〜を達成する、遂げる」", "choices": ["Accomplish", "Accompany", "Accumulate", "Accommodate"], "answer": "Accommodate", "hint": "ミッションを完遂する、といった場面で使います"},
        {"question": "「（仕事など）を引き受ける、担当する」", "choices": ["Undertake", "Understand", "Undergo", "Underline"], "answer": "Undertake", "hint": "責任を持ってそのタスクを背負うイメージです"},
        {"question": "「〜を承認する、賛成する」", "choices": ["Approve", "Appoint", "Appeal", "Apply"], "answer": "Approve", "hint": "上司から「承認（Approval）」をもらうの動詞形です"},
        {"question": "「義務的な、強制的な」", "choices": ["Mandatory", "Magnificent", "Maximum", "Marginal"], "answer": "Mandatory", "hint": "ビジネスの研修などで「必須受講」の際によく使われます"},
        {"question": "「同僚」", "choices": ["Colleague", "Collection", "College", "Collision"], "answer": "Colleague", "hint": "職場で一緒に働く仲間のことです"},
        {"question": "「〜を実行する、導入する」", "choices": ["Implement", "Implicate", "Impress", "Import"], "answer": "Implement", "hint": "計画や新しいシステムを実際の行動に移すことです"},
        {"question": "「履歴書」", "choices": ["Resume", "Result", "Resource", "Research"], "answer": "Resume", "hint": "レジュメ。就職活動で必ず提出する書類です"},
        {"question": "「利益、収益」", "choices": ["Profit", "Product", "Promotion", "Project"], "answer": "Profit", "hint": "プロフィット。売上からコストを引いた儲けのことです"}
    ]
}

# --- アプリの状態・ユーザーデータの管理 ---
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""

# ステータス
if 'exp' not in st.session_state:
    st.session_state.exp = 350
if 'level' not in st.session_state:
    st.session_state.level = 2
if 'streak' not in st.session_state:
    st.session_state.streak = 5

if 'completed_dates' not in st.session_state:
    st.session_state.completed_dates = { (datetime.date.today() - datetime.timedelta(days=1)).isoformat() }

# --- クイズ用状態管理 ---
if 'current_category' not in st.session_state:
    st.session_state.current_category = list(QUIZ_CATEGORIES.keys())[0]
if 'quiz_index' not in st.session_state:
    st.session_state.quiz_index = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'show_answer_screen' not in st.session_state:
    st.session_state.show_answer_screen = False  # 答え合わせ画面フラグ
if 'selected_answer' not in st.session_state:
    st.session_state.selected_answer = ""

# =============================================================
# 🔐 ログイン / 新規登録 画面
# =============================================================
if not st.session_state.is_logged_in:
    st.title("🦉 E-Lingo へようこそ！")
    st.subheader("英語学習を継続して、ネイティブを目指そう")
    
    auth_tab1, auth_tab2 = st.tabs(["🔒 ログイン", "📝 新規アカウント登録"])
    
    with auth_tab1:
        st.write("登録したアカウントでログインしてください。")
        login_user = st.text_input("ユーザー名（ログイン用）", key="login_user")
        login_pass = st.text_input("パスワード（ログイン用）", type="password", key="login_pass")
        
        if st.button("ログインする"):
            if login_user in st.session_state.user_db and st.session_state.user_db[login_user] == login_pass:
                st.session_state.is_logged_in = True
                st.session_state.current_user = login_user
                st.success(f"ログイン成功！ おかえりなさい、{login_user} さん！")
                st.rerun()
            else:
                st.error("❌ ユーザー名またはパスワードが正しくありません。")
                
    with auth_tab2:
        st.write("新しいアカウントを作成します。（PCを再起動しても保存されます）")
        new_user = st.text_input("希望するユーザー名", key="new_user")
        new_pass = st.text_input("希望するパスワード", type="password", key="new_pass")
        confirm_pass = st.text_input("パスワード（確認用）", type="password", key="confirm_pass")
        
        if st.button("アカウントを作成する"):
            if not new_user or not new_pass:
                st.warning("⚠️ ユーザー名とパスワードを入力してください。")
            elif new_user in st.session_state.user_db:
                st.error("❌ そのユーザー名は既に使われています。別の名前を入力してください。")
            elif new_pass != confirm_pass:
                st.error("❌ パスワードが一致しません。もう一度確認してください。")
            else:
                st.session_state.user_db[new_user] = new_pass
                save_users(st.session_state.user_db)
                st.success("🎉 アカウント登録が完了しました！「ログイン」タブからログインしてください。")

# =============================================================
# 🦉 メインアプリ画面（ログイン後のみ表示）
# =============================================================
else:
    st.sidebar.title("🦉 E-Lingo メニュー")
    st.sidebar.write(f"👤 ユーザー: **{st.session_state.current_user}**")
    
    page = st.sidebar.radio("画面を切り替える", [
        "🟢 今日の学習ダッシュボード", 
        "🎯 3大問・英単語クイズ", 
        "📅 継続カレンダー",
        "📊 学習の進捗・分析", 
        "🏆 獲得したトロフィー"
    ])
    
    st.sidebar.write("---")
    if st.sidebar.button("🚪 ログアウト"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    # --- 1. 今日の学習ダッシュボード ---
    if page == "🟢 今日の学習ダッシュボード":
        st.title(f"🦉 Welcome back, {st.session_state.current_user}!")
        st.subheader("今日も英語の習慣を続けましょう！")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="現在のレベル", value=f"Lv. {st.session_state.level}")
        with col2:
            st.metric(label="合計経験値", value=f"✨ {st.session_state.exp} EXP")
        with col3:
            st.metric(label="連続達成日数", value=f"🔥 {st.session_state.streak} 日連続！")
            
        next_level_exp = 1000
        progress_val = min(st.session_state.exp / next_level_exp, 1.0)
        st.progress(progress_val, text=f"次のレベル（Lv.{st.session_state.level + 1}）まであと {next_level_exp - st.session_state.exp} EXP！")

    # --- 2. 3大問・英単語クイズ（回答後に判定を挟む新システム） ---
    elif page == "🎯 3大問・英単語クイズ":
        st.title("🎯 英単語実力テスト")
        
        chosen_cat = st.selectbox(
            "挑戦する大問（カテゴリー）を選択してください：", 
            list(QUIZ_CATEGORIES.keys()),
            index=list(QUIZ_CATEGORIES.keys()).index(st.session_state.current_category)
        )
        
        if chosen_cat != st.session_state.current_category:
            st.session_state.current_category = chosen_cat
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_completed = False
            st.session_state.show_answer_screen = False
            st.rerun()

        current_quiz_list = QUIZ_CATEGORIES[st.session_state.current_category]

        if st.session_state.quiz_completed:
            st.success(f"🎉 {st.session_state.current_category} の全10問を完了しました！")
            st.metric(label="今回の大問スコア", value=f"{st.session_state.quiz_score} / 10 問正解")
            
            if st.button("この大問に再挑戦する"):
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_completed = False
                st.session_state.show_answer_screen = False
                st.rerun()
        else:
            current_q = current_quiz_list[st.session_state.quiz_index]
            
            # 🔄 答え合わせ（リザルト画面）モード
            if st.session_state.show_answer_screen:
                st.info(f"📝 問題 {st.session_state.quiz_index + 1} / {len(current_quiz_list)} の答え合わせ")
                st.write(f"**問題:** {current_q['question']}")
                st.write(f"あなたの回答: **{st.session_state.selected_answer}**")
                
                if st.session_state.selected_answer == current_q["answer"]:
                    st.success(f"⭕ 正解！「{current_q['answer']}」で大正解です！")
                else:
                    st.error(f"❌ 不正解... 正解は「{current_q['answer']}」でした。")
                
                # 次へ進むためのボタン
                button_text = "結果を確認して終了する 🏁" if st.session_state.quiz_index == len(current_quiz_list) - 1 else "次へ進む ➡️"
                if st.button(button_text):
                    # スコアの加算
                    if st.session_state.selected_answer == current_q["answer"]:
                        st.session_state.quiz_score += 1
                    
                    # 最終問題だった場合
                    if st.session_state.quiz_index == len(current_quiz_list) - 1:
                        st.session_state.quiz_completed = True
                        st.session_state.exp += st.session_state.quiz_score * 25
                        st.session_state.completed_dates.add(datetime.date.today().isoformat())
                        st.balloons()
                    else:
                        st.session_state.quiz_index += 1
                        
                    st.session_state.show_answer_screen = False
                    st.rerun()
                    
            # 📝 通常の回答選択モード
            else:
                progress_percent = (st.session_state.quiz_index) / len(current_quiz_list)
                st.progress(progress_percent, text=f"問題 {st.session_state.quiz_index + 1} / {len(current_quiz_list)}")
                
                st.info(f"💡 **問題:** {current_q['question']} という意味の英単語はどれ？")
                
                # 最初は何も選んでいない状態
                options_with_default = ["（選択してください）"] + current_q["choices"]
                choice = st.radio(
                    "正しいと思うものを選択してください：", 
                    options_with_default, 
                    index=0,
                    key=f"q_{chosen_cat}_{st.session_state.quiz_index}"
                )
                
                with st.expander("💡 ヒントを見る"):
                    st.write(current_q["hint"])
                
                # 何か選んだら「次へ」ボタンが活性化
                if choice != "（選択してください）":
                    if st.button("この回答で次へ進む ➡️"):
                        st.session_state.selected_answer = choice
                        st.session_state.show_answer_screen = True
                        st.rerun()

    # --- 3. 📅 継続カレンダー ---
    elif page == "📅 継続カレンダー":
        st.title("📅 学習継続カレンダー")
        st.subheader("クイズを1回でもクリアした日に「✅」が記録されます！")
        
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=14)
        
        st.write("### 直近の学習状況")
        
        cols = st.columns(7)
        for i in range(14):
            current_date = start_date + datetime.timedelta(days=i)
            date_str = current_date.isoformat()
            weekday_str = ["月", "火", "水", "木", "金", "土", "日"][current_date.weekday()]
            label = f"{current_date.month}/{current_date.day}({weekday_str})"
            
            with cols[i % 7]:
                if date_str in st.session_state.completed_dates:
                    st.success(f"**{label}**\n\n🎉 CLEAR!")
                else:
                    if current_date == today:
                        st.info(f"**{label}**\n\n👀 未挑戦")
                    else:
                        st.button(f"**{label}**\n\n💤 お休み", disabled=True, key=f"date_{date_str}")
        
        st.write("---")
        st.metric(label="トータル学習日数", value=f"📊 {len(st.session_state.completed_dates)} 日間")

    # --- 4. 学習の進捗・分析 ---
    elif page == "📊 学習の進捗・分析":
        st.title("📊 学習の振り返りグラフ")
        chart_data = pd.DataFrame({
            '曜日': ['月', '火', '水', '木', '金', '土', '日'],
            '学習時間(分)': [15, 20, 10, 25, 0, 30, 15]
        })
        fig = px.line(chart_data, x='曜日', y='学習時間(分)', title='今週の英語学習の推移', markers=True)
        st.plotly_chart(fig)

    # --- 5. 獲得したトロフィー ---
    elif page == "🏆 獲得したトロフィー":
        st.title("🏆 実績（アチーブメント）")
        col1, col2 = st.columns(2)
        with col1:
            st.success("🥚 **最初の一歩**\n\n初めてクイズに正解した（達成済み）")
            st.success("🔥 **三日坊主を突破**\n\n3日連続で学習した（達成済み）")
        with col2:
            st.info("🦉 **語彙力の鬼**\n\nいずれかの大問で10問全問正解する（未解放）")
            st.warning("🔒 **ネイティブへの道**\n\n合計1000 EXPを獲得する（未解放）")