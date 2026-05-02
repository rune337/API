# IAM CLI 設計の考え方

この資料は、「どこから考えて、どうプログラムを作ればいいか」を説明するためのものです。
コードの細かい説明は `STUDY_GUIDE.md`、コマンドの使い方は `COMMAND_MANUAL.md` を見ます。
config.yaml の詳しい書き方は `CONFIG_WRITING_GUIDE.md` を見ます。

## 1. まず目的を一文で決める

最初に、作りたいものを短く言えるようにします。

このプロジェクトなら目的はこうです。

```text
複数アカウントに対して、IAMのユーザー、グループ、ポリシーをコマンドで操作できるようにする。
```

ここで大事なのは、いきなりコードを書かないことです。
まず「何を操作したいのか」を言葉にします。

今回の対象はこれです。

```text
ユーザー
グループ
ポリシー
ユーザーとポリシーの関連
グループとポリシーの関連
```

## 2. 操作を一覧にする

次に、対象ごとに必要な操作を書き出します。

```text
ユーザー
  一覧
  作成
  削除

グループ
  一覧
  作成
  削除

ポリシー
  一覧
  内容取得
  作成
  更新
  削除

ユーザーとポリシー
  追加
  削除

グループとポリシー
  追加
  削除
```

この一覧が、あとでコマンドファイルになります。

```text
ユーザー一覧
  list_users.py

ユーザー作成
  create_user.py

ポリシー更新
  update_policy.py
```

「操作一覧を書く」ことで、作るファイルが見えてきます。

## 3. 入力方法を決める

プログラムは、何かを入力として受け取って動きます。
今回の入力方法は2つあります。

```text
1. コマンド引数で直接指定する
2. config.yaml から読む
```

なぜ2つ必要かを考えます。

### コマンド引数が向いているもの

一回だけ試したい値に向いています。

```bash
python3 create_user.py --user test-user ...
```

例えば、今だけ `test-user` を作りたい時です。

### config.yaml が向いているもの

何度も使う設定に向いています。

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
```

アカウントID、キー、よく使うポリシーARN、作成ユーザー一覧などは、毎回コマンドに書くと大変です。
なのでconfigに置きます。

## 4. 優先順位を決める

入力方法が複数ある場合は、どちらを優先するかを決めます。

このプロジェクトではこうしました。

```text
CLIで指定した値を優先する
CLIに無ければ config.yaml から読む
```

理由は、普段はconfigを使いながら、今回だけ別の値で試すことができるからです。

例:

```bash
python3 update_policy.py --config ./config.yaml --policy-file ../B.json
```

configには `../A.json` が書いてあっても、この実行ではCLIの `../B.json` を使います。

## 5. 変わる部分と共通部分を分ける

いろいろなコマンドを見比べると、同じ処理がたくさんあります。

共通しているもの:

```text
引数を読む
configを読む
対象アカウントを絞る
アカウントにログインする
アカウントごとに繰り返す
```

コマンドごとに違うもの:

```text
ユーザーを作る
グループを消す
ポリシーを更新する
ポリシーをユーザーに付ける
```

このように分けて考えると、ファイル構成が決まります。

```text
iamcli_common.py
  共通処理

iamfunction.py
  IAM API操作

create_user.py など
  コマンドごとの処理
```

## 6. API操作を専用ファイルに集める

AWS IAMに対する操作は `iamfunction.py` に集めます。

理由は、各コマンドファイルに直接 boto3 の処理を書くと、あとで修正が大変になるからです。

悪い例:

```text
create_user.py に iam.create_user()
delete_user.py に iam.delete_user()
update_policy.py に iam.create_policy_version()
```

これでも動きますが、処理が散らばります。

今回の形:

```text
create_user.py
  iamfunction.create_user() を呼ぶ

delete_user.py
  iamfunction.delete_user() を呼ぶ

update_policy.py
  iamfunction.update_policy() を呼ぶ
```

こうすると、IAM APIのことを調べたい時は `iamfunction.py` を見ればよくなります。

## 7. まず一番小さい機能から作る

いきなり全部作ると混乱します。
最初は一番簡単な機能から作ります。

おすすめの順番:

```text
1. login()
2. list_users.py
3. create_user.py
4. config.yaml対応
5. 複数アカウント対応
6. グループ対応
7. ポリシー対応
8. attach / detach対応
```

最初に `list_users.py` を作る理由は、データを壊しにくいからです。
一覧取得は読み取りだけなので、テストしやすいです。

次に `create_user.py` を作ります。
作成できたら、もう一度 `list_users.py` で確認できます。

```text
作る
  create_user.py

確認する
  list_users.py
```

このように、作成系と確認系をセットで考えます。

## 8. 1つのコマンドの作り方

新しいコマンドを作る時は、毎回この順番で考えます。

```text
1. コマンド名を決める
2. 必要な引数を決める
3. configではどのキーから読むか決める
4. iamfunction.py にAPI関数を作る
5. コマンドファイルからAPI関数を呼ぶ
6. --help と構文チェックを確認する
```

例として、グループ作成を考えます。

### 1. コマンド名

```text
create_group.py
```

### 2. 必要な引数

```text
--group
```

### 3. configのキー

```yaml
create_groups:
  - group-a
```

### 4. IAM API関数

```python
def create_group(group_name, iam):
    iam.create_group(GroupName=group_name)
```

### 5. コマンド側

```python
for group_name in groups:
    iamfunction.create_group(group_name, iam)
```

このように、1つずつ決めると迷いにくくなります。

## 9. 削除処理は先に関連を考える

削除は作成より注意が必要です。

例えばIAMユーザーは、ユーザーだけ削除しようとしても失敗することがあります。
アクセスキーやポリシーやグループ所属が残っているからです。

だから削除処理は、先に関連を外します。

```text
ユーザー削除
  アクセスキー削除
  ユーザーポリシー解除
  グループから外す
  ユーザー削除
```

グループ削除も同じです。

```text
グループ削除
  グループ内ユーザーを外す
  グループポリシー解除
  グループ削除
```

削除系を作る時は、「本体を消す前に何を外す必要があるか」を考えます。

## 10. ポリシー更新は「上書き」ではなく「新バージョン」

IAMのマネージドポリシーは、JSONを直接上書きするのではありません。

考え方はこうです。

```text
新しいポリシーバージョンを作る
そのバージョンをデフォルトにする
古いバージョンを消す
```

だから `update_policy.py` は、内部では `create_policy_version()` を使います。

```python
iam.create_policy_version(
    PolicyArn=policy_arn,
    PolicyDocument=policy_document,
    SetAsDefault=True,
)
```

この仕様を知らないと、「updateなのにcreateを呼ぶのはなぜ」と混乱します。
IAMではこれが自然な更新方法です。

## 11. config.yamlの設計

configは、アカウントごとに必要な情報をまとめます。

基本形:

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
```

そこに、コマンドごとの対象を書きます。

```yaml
create_users:
  - user-a

create_groups:
  - group-a

policies:
  aa:
    arn: arn:aws:iam::111111111111:policy/aa
    file: ../A.json
```

`policies` は、ポリシー名からARNやJSONファイルを引くための辞書です。

```yaml
policies:
  aa:
    arn: ...
    file: ...
```

こうしておくと、コマンドでは `aa` という名前だけで扱えます。

```yaml
update_policies:
  - policy_name: aa
```

## 12. エラー設計

エラーは、初心者でも次に何をすればいいか分かる文にします。

例:

```text
入力エラー: configなしの場合、--user を指定してください
```

これは良いエラーです。
理由は、足りないものが分かるからです。

悪いエラー:

```text
KeyError: user
```

これだけだと、どこを直せばいいか分かりにくいです。

だから、コマンド側では必要な値がない時に、なるべく分かるメッセージを出します。

## 13. 動作確認の考え方

動作確認は、いきなり全部を試しません。
小さい順に確認します。

```text
1. 構文チェック
2. --help が出るか
3. 入力不足の時に分かるエラーが出るか
4. motoサーバーに接続して一覧取得
5. 作成
6. 一覧で確認
7. 削除
8. 一覧で確認
```

構文チェック:

```bash
python3 -m py_compile *.py
```

ヘルプ確認:

```bash
python3 create_user.py --help
```

motoサーバー:

```bash
python3 -m moto.server -H 127.0.0.1 -p 5000
```

## 14. 新しい機能を追加する時のテンプレート

新しいIAM操作を追加する時は、この型で考えます。

```text
やりたいこと:
  例: ユーザーをグループに追加したい

必要な入力:
  user_name
  group_name

configに書くキー:
  add_users_to_groups

iamfunction.pyに作る関数:
  add_user_to_group(user_name, group_name, iam)

コマンドファイル:
  add_user_to_group.py

確認方法:
  get_group または list_groups_for_user
```

このテンプレートに当てはめると、次に何を作ればいいかが見えます。

## 15. このプロジェクトで大事な判断

このプロジェクトで大事な設計判断は次の3つです。

```text
1. IAM API操作は iamfunction.py に集める
2. CLI/config/ログイン/繰り返しは iamcli_common.py に集める
3. 各コマンドファイルは薄くする
```

各コマンドファイルが薄いと、読みやすくなります。

理想はこうです。

```text
引数を定義する
configやCLIから対象を決める
iamfunctionの関数を呼ぶ
結果をprintする
```

これ以上複雑になったら、共通処理かAPI処理として別ファイルに逃がすことを考えます。

## 16. 迷った時の考え方

迷ったら、次の順に考えます。

```text
1. これはIAM API操作か？
   はい → iamfunction.py

2. これは複数コマンドで使う処理か？
   はい → iamcli_common.py

3. これは特定コマンドだけの処理か？
   はい → そのコマンドファイル

4. これは毎回変わる値か？
   はい → CLIオプション

5. これは何度も使う設定か？
   はい → config.yaml
```

この判断基準があると、どこにコードを書くか決めやすくなります。

## 17. まとめ

プログラムは、いきなり書くよりも、次の順番で考えると作りやすいです。

```text
目的を一文にする
対象を分ける
操作を一覧にする
入力方法を決める
共通部分と違う部分を分ける
小さい機能から作る
確認できるコマンドを先に作る
削除や更新は関連するものを考える
```

このプロジェクトでは、その考え方がこの形になっています。

```text
iamfunction.py
  IAM API操作

iamcli_common.py
  共通のCLI処理

各コマンド.py
  具体的な操作

config.yaml
  何度も使う設定
```
