# IAM CLI 学習資料

この資料は、各プログラムがどのように動いているかを勉強するための説明です。
コマンドの実行例は `COMMAND_MANUAL.md`、コードの仕組みはこの資料、という使い分けです。
プログラムをどう設計するかは `DESIGN_THINKING_GUIDE.md` にあります。
config.yaml の詳しい書き方は `CONFIG_WRITING_GUIDE.md` にあります。
YAMLの基本文法は `YAML_GUIDE.md` にあります。

## 全体像

このプロジェクトは、役割を3つに分けています。

```text
各コマンドファイル
  create_user.py
  list_users.py
  update_policy.py
  ...

共通CLI処理
  iamcli_common.py

AWS IAM API操作
  iamfunction.py
```

各コマンドファイルは、引数を受け取り、対象アカウントごとに処理を実行します。
実際のIAM API呼び出しは、できるだけ `iamfunction.py` に集めています。

## 処理の流れ

代表例として、ユーザー作成はこう流れます。

```text
python3 create_user.py ...
  ↓
argparse でオプションを読む
  ↓
iamcli_common.run_for_accounts()
  ↓
config または直接指定からアカウント情報を作る
  ↓
iamcli_common.login_account()
  ↓
iamfunction.login() または iamfunction.login_as_account()
  ↓
iamfunction.create_user()
  ↓
boto3 の iam.create_user() / iam.create_access_key()
```

この形にしている理由は、ユーザー作成、グループ作成、ポリシー更新などで、アカウント読み込みやログイン処理を毎回書かなくて済むようにするためです。

## iamfunction.py

`iamfunction.py` は、IAM APIを直接呼ぶ関数をまとめたファイルです。

### login()

```python
def login(aws_access_key_id, aws_secret_access_key):
```

アクセスキーとシークレットキーでIAMクライアントを作ります。
`endpoint_url=URL` があるので、今は `http://127.0.0.1:5000` のmotoに接続します。

### login_as_account()

```python
def login_as_account(account_id):
```

motoでアカウント分離を検証するためのログインです。
STSの `assume_role()` を使い、指定した `account_id` の認証情報を作ってからIAMクライアントを返します。

keyだけでmotoを使うと同じデフォルトアカウントを見やすいので、アカウントごとに分けたい時はこの関数を使います。

### list_all_users()

IAMユーザー一覧を取得します。

```python
paginator = iam.get_paginator('list_users')
```

一覧APIは件数が多いと複数ページになるため、paginatorを使っています。

### create_user()

ユーザーを作成し、アクセスキーも作ります。

```text
iam.create_user()
iam.create_access_key()
```

既にユーザーが存在する場合は、エラーで止めずに「スキップ」として返します。

### delete_user()

ユーザー削除前に、削除の邪魔になるものを外します。

```text
アクセスキーを削除
ユーザーに付いたポリシーをdetach
所属グループからremove
ユーザー削除
```

IAMでは、ユーザーにアクセスキーやポリシーが残っていると削除できないことがあるためです。

### group系関数

グループは以下の関数で操作します。

```text
list_all_groups()
create_group()
delete_group()
```

`delete_group()` は、削除前にユーザーをグループから外し、グループに付いたポリシーもdetachします。

### policy系関数

ポリシーは以下の関数で操作します。

```text
list_all_policies()
get_policy_document()
create_policy()
delete_policy()
update_policy()
```

`create_policy()` は、JSONファイルやJSON文字列から読んだ内容を `iam.create_policy()` に渡します。

`update_policy()` は、既存ポリシーに新しいバージョンを作ります。
このプロジェクトでは、更新後に古い非デフォルトバージョンを削除し、新しいデフォルトバージョンだけ残す動きにしています。

### attach / detach系関数

ポリシーをユーザーやグループに付け外しします。

```text
attach_user_policy()
detach_user_policy()
attach_group_policy()
detach_group_policy()
```

中ではそれぞれ `iam.attach_user_policy()` や `iam.detach_group_policy()` を呼んでいます。

## iamcli_common.py

`iamcli_common.py` は、各コマンドで共通する処理をまとめたファイルです。

### add_account_args()

すべてのコマンドで共通の引数を追加します。

```text
--config
--account
--use-account-id
--account-id
--access-key
--secret-key
```

これにより、どのコマンドでも同じ指定方法が使えます。

### get_accounts()

アカウント情報を作ります。

```text
--config あり
  config.yaml から accounts を読む

--config なし
  コマンド引数から1つのアカウント情報を作る
```

### run_for_accounts()

このプロジェクトでかなり重要な関数です。

```python
def run_for_accounts(args, process):
```

指定されたアカウントを順番に処理します。
各コマンドは `process(account, iam)` という関数を作って、この `run_for_accounts()` に渡します。

イメージ:

```python
for account in accounts:
    iam = login_account(account, args.use_account_id)
    process(account, iam)
```

### load_json_arg()

ポリシーJSONを読みます。

```text
--policy-file があればファイルから読む
--policy-json があれば文字列をJSONとして読む
```

### get_policy_arn()

ポリシーARNを取得します。

優先順位はこうです。

```text
1. CLIの --policy-arn
2. config内の arn / policy_arn
3. config内の policies で名前から検索
```

つまり、CLIで直接ARNを渡すことも、configに書いた名前からARNを引くこともできます。

### load_policy_document()

ポリシー内容を取得します。

優先順位はこうです。

```text
1. CLIの --policy-file / --policy-json
2. 対象設定の file / json
3. policies に書かれた file / json
```

これにより、`--config` だけでポリシー作成や更新ができます。

## config.yaml

`config.yaml` は、アカウントごとの設定を書きます。

例:

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
    create_users:
      - user-a
      - user-b
    create_groups:
      - group-a
    policies:
      aa:
        arn: arn:aws:iam::111111111111:policy/aa
        file: ../A.json
    update_policies:
      - policy_name: aa
        file: ../A.json
```

`--config` を使うと、各コマンドはこの情報を読みます。
ただし、CLIで指定した値がある場合はCLIが優先されます。

## 各コマンド

### list_users.py

ユーザー一覧を表示します。

主な処理:

```text
iamfunction.list_all_users(iam)
```

表示するだけなので、configに `create_users` などを書く必要はありません。

### create_user.py

ユーザーを作成します。

入力元:

```text
CLI: --user
config: create_users
```

CLIの `--user` がある場合は、configの `create_users` より優先されます。

呼び出すAPI関数:

```text
iamfunction.create_user()
```

### delete_user.py

ユーザーを削除します。

入力元:

```text
CLI: --user
config: delete_users
```

呼び出すAPI関数:

```text
iamfunction.delete_user()
```

削除時にアクセスキー、ユーザーポリシー、グループ所属も整理します。

### list_groups.py

グループ一覧を表示します。

呼び出すAPI関数:

```text
iamfunction.list_all_groups()
```

### create_group.py

グループを作成します。

入力元:

```text
CLI: --group
config: create_groups
```

呼び出すAPI関数:

```text
iamfunction.create_group()
```

### delete_group.py

グループを削除します。

入力元:

```text
CLI: --group
config: delete_groups
```

呼び出すAPI関数:

```text
iamfunction.delete_group()
```

削除前に、グループ内ユーザーと付与ポリシーを外します。

### list_policies.py

ポリシー一覧を表示します。

呼び出すAPI関数:

```text
iamfunction.list_all_policies()
```

この一覧ではポリシーの内容やバージョン数までは表示しません。
内容を見る場合は `get_policy.py` を使います。

### get_policy.py

ポリシー内容を表示します。

入力元:

```text
CLI: --policy-arn / --policy-name
config: policies
```

呼び出すAPI関数:

```text
iamfunction.get_policy_document()
```

`--version-id` を指定しない場合は、デフォルトバージョンの内容を表示します。

### create_policy.py

ポリシーを新規作成します。

入力元:

```text
CLI: --policy-name + --policy-file / --policy-json
config: create_policies または policies
```

呼び出すAPI関数:

```text
iamfunction.create_policy()
```

これはローカルにJSONを作るコマンドではありません。
ローカルのJSONファイルを読み込み、IAMに新規ポリシーとして作成します。

### update_policy.py

既存ポリシーを更新します。

入力元:

```text
CLI: --policy-arn / --policy-name + --policy-file / --policy-json
config: update_policies または policies
```

呼び出すAPI関数:

```text
iamfunction.update_policy()
```

更新時は新しいポリシーバージョンを作り、デフォルトにします。
その後、古い非デフォルトバージョンを削除します。

### delete_policy.py

ポリシーを削除します。

入力元:

```text
CLI: --policy-arn / --policy-name
config: delete_policies または policies
```

呼び出すAPI関数:

```text
iamfunction.delete_policy()
```

削除前に、ユーザー、グループ、ロールからポリシーをdetachします。
その後、非デフォルトのポリシーバージョンを削除してからポリシー本体を削除します。

### attach_user_policy.py

ユーザーにポリシーを追加します。

入力元:

```text
CLI: --user + --policy-arn / --policy-name
config: attach_user_policies
```

呼び出すAPI関数:

```text
iamfunction.attach_user_policy()
```

configでは次のように書けます。

```yaml
attach_user_policies:
  - user: user-a
    policy: aa
```

この `policy: aa` は、同じアカウント内の `policies.aa` を参照します。

### detach_user_policy.py

ユーザーからポリシーを削除します。

入力元:

```text
CLI: --user + --policy-arn / --policy-name
config: detach_user_policies
```

呼び出すAPI関数:

```text
iamfunction.detach_user_policy()
```

### attach_group_policy.py

グループにポリシーを追加します。

入力元:

```text
CLI: --group + --policy-arn / --policy-name
config: attach_group_policies
```

呼び出すAPI関数:

```text
iamfunction.attach_group_policy()
```

### detach_group_policy.py

グループからポリシーを削除します。

入力元:

```text
CLI: --group + --policy-arn / --policy-name
config: detach_group_policies
```

呼び出すAPI関数:

```text
iamfunction.detach_group_policy()
```

## main.py と listuser.py

この2つは互換用です。

```text
main.py
  create_user.py を呼ぶ

listuser.py
  list_users.py を呼ぶ
```

以前の名前で実行しても動くように残しています。

## create_policy_json.py

CSVからポリシーJSONを生成する補助プログラムです。

役割:

```text
policy.csv を読む
ポリシーJSONを組み立てる
Json ディレクトリに出力する
```

IAMにポリシーを作成するわけではありません。
作成したJSONを `create_policy.py --policy-file ...` に渡すことで、IAM側にポリシーを作成できます。

## create_policy_json_simple.py

より簡単なCSV形式からポリシーJSONを生成する補助プログラムです。

こちらもIAM APIは呼びません。
ローカルにJSONファイルを作るだけです。

## 読む順番のおすすめ

最初はこの順番で読むと分かりやすいです。

```text
1. config.yaml
2. create_user.py
3. iamcli_common.py の run_for_accounts()
4. iamfunction.py の login() / login_as_account()
5. iamfunction.py の create_user()
6. update_policy.py
7. iamcli_common.py の get_policy_arn() / load_policy_document()
```

ユーザー作成は一番シンプルです。
その後にポリシー更新を見ると、configからARNやJSONファイルを補完する流れが理解しやすくなります。

## よくある理解ポイント

### CLI指定とconfig指定の優先順位

CLIで指定した値が優先です。

```bash
python3 update_policy.py --config ./config.yaml --policy-file ../B.json ...
```

この場合、configに `file: ../A.json` があっても、CLIの `../B.json` が使われます。

### motoでアカウント分離したい場合

`--use-account-id` を付けます。

```bash
python3 list_users.py --config ./config.yaml --use-account-id
```

これを付けない場合、keyログインになり、motoでは同じデフォルトアカウントを見ることがあります。

### ポリシー一覧とポリシー内容

`list_policies.py` は一覧だけです。

```text
ポリシー名
ARN
```

内容を見る場合は `get_policy.py` を使います。

### ポリシー更新とバージョン

IAMのポリシー更新は、既存JSONを書き換えるのではなく、新しいポリシーバージョンを作ります。
このプロジェクトでは、更新後に古いバージョンを削除して、新しい1つだけ残すようにしています。
