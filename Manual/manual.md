# IAMコマンド マニュアル

## motoサーバー起動

別ターミナルで先に起動します。

```bash
python3 -m moto.server -H 127.0.0.1 -p 5000
```

## 基本

このコマンドは、デフォルトではYAMLを読みません。
引数でアカウント情報と作成ユーザーを直接指定します。

```bash
python3 main.py --use-account-id --account account-a --account-id 111111111111 --user test-user
```

実行すると、作成結果を標準出力に表示します。

## motoのアカウントID分離で作成

motoでアカウントごとに分離して検証したい場合は、`--use-account-id` と `--account-id` を使います。

```bash
python3 main.py --use-account-id --account account-a --account-id 111111111111 --user test-user
```

複数ユーザーを作る場合は、`--user` を複数指定します。

```bash
python3 main.py --use-account-id --account account-a --account-id 111111111111 --user user-a --user user-b
```

## keyログインで作成

アクセスキーとシークレットキーでログインする場合は、`--access-key` と `--secret-key` を指定します。

```bash
python3 main.py --account account-a --access-key test --secret-key test --user test-user
```

複数ユーザーを作る場合:

```bash
python3 main.py --account account-a --access-key test --secret-key test --user user-a --user user-b
```

## YAMLを使って作成

YAMLを使う場合だけ、`--config` を指定します。

```bash
python3 main.py --config ./config.yaml
```

`config.yaml` の例:

```yaml
accounts:
  - name: account-a
    account_id: '111111111111'
    access_key: test
    secret_key: test
    create_users:
      - user-a
      - user-b

  - name: account-b
    account_id: '222222222222'
    access_key: test
    secret_key: test
    create_users:
      - user-c
```

## YAMLから一部アカウントだけ作成

`--account` で対象アカウントを絞り込めます。

```bash
python3 main.py --config ./config.yaml --account account-a
```

複数アカウントを指定する場合:

```bash
python3 main.py --config ./config.yaml --account account-a --account account-b
```

## YAML + 今回だけユーザー指定

`--user` を指定すると、YAML内の `create_users` より優先されます。

```bash
python3 main.py --config ./config.yaml --account account-a --user test-user
```

複数ユーザー:

```bash
python3 main.py --config ./config.yaml --account account-a --user user-a --user user-b
```

## YAML + motoアカウントID分離

YAMLの `account_id` を使ってmotoのアカウント分離を検証する場合:

```bash
python3 main.py --config ./config.yaml --use-account-id
```

一部アカウントだけ:

```bash
python3 main.py --config ./config.yaml --use-account-id --account account-a
```

## オプション一覧

| オプション | 意味 |
| --- | --- |
| `--config` | 読み込むYAMLファイル |
| `--account` | 対象アカウント名。複数指定可能 |
| `--user` | 作成するユーザー名。複数指定可能 |
| `--use-account-id` | motoのアカウントID分離を使う |
| `--account-id` | 直接指定時に使うmotoアカウントID |
| `--access-key` | keyログイン用アクセスキー |
| `--secret-key` | keyログイン用シークレットキー |

## コマンド一覧

| 操作 | コマンド |
| --- | --- |
| ユーザー一覧 | `python3 list_users.py ...` |
| ユーザー作成 | `python3 create_user.py ...` |
| ユーザー削除 | `python3 delete_user.py ...` |
| グループ一覧 | `python3 list_groups.py ...` |
| グループ作成 | `python3 create_group.py ...` |
| グループ削除 | `python3 delete_group.py ...` |
| ポリシー一覧 | `python3 list_policies.py ...` |
| ポリシー作成 | `python3 create_policy.py ...` |
| ポリシー削除 | `python3 delete_policy.py ...` |
| ポリシー更新 | `python3 update_policy.py ...` |
| ユーザーにポリシー追加 | `python3 attach_user_policy.py ...` |
| ユーザーからポリシー削除 | `python3 detach_user_policy.py ...` |
| グループにポリシー追加 | `python3 attach_group_policy.py ...` |
| グループからポリシー削除 | `python3 detach_group_policy.py ...` |

`main.py` は互換用に `create_user.py` と同じ動きをします。
`listuser.py` は互換用に `list_users.py` と同じ動きをします。

## 共通指定

直接指定でmotoアカウントID分離:

```bash
python3 list_users.py --use-account-id --account account-a --account-id 111111111111
```

直接指定でkeyログイン:

```bash
python3 list_users.py --account account-a --access-key test --secret-key test
```

YAMLから読み込み:

```bash
python3 list_users.py --config ./config.yaml --use-account-id
```

YAMLから一部アカウントだけ:

```bash
python3 list_users.py --config ./config.yaml --use-account-id --account account-a
```

## 各コマンド例

ユーザー作成:

```bash
python3 create_user.py --use-account-id --account account-a --account-id 111111111111 --user user-a
```

ユーザー削除:

```bash
python3 delete_user.py --use-account-id --account account-a --account-id 111111111111 --user user-a
```

グループ作成:

```bash
python3 create_group.py --use-account-id --account account-a --account-id 111111111111 --group group-a
```

グループ一覧:

```bash
python3 list_groups.py --use-account-id --account account-a --account-id 111111111111
```

グループ削除:

```bash
python3 delete_group.py --use-account-id --account account-a --account-id 111111111111 --group group-a
```

ポリシー一覧:

```bash
python3 list_policies.py --use-account-id --account account-a --account-id 111111111111
```

ポリシー作成:

```bash
python3 create_policy.py --use-account-id --account account-a --account-id 111111111111 --policy-name test-policy --policy-file ./policy.json
```

ポリシー削除:

```bash
python3 delete_policy.py --use-account-id --account account-a --account-id 111111111111 --policy-arn arn:aws:iam::111111111111:policy/test-policy
```

ポリシー更新:

```bash
python3 update_policy.py --use-account-id --account account-a --account-id 111111111111 --policy-arn arn:aws:iam::111111111111:policy/test-policy --policy-file ./policy.json
```

ユーザーにポリシー追加:

```bash
python3 attach_user_policy.py --use-account-id --account account-a --account-id 111111111111 --user user-a --policy-arn arn:aws:iam::111111111111:policy/test-policy
```

ユーザーからポリシー削除:

```bash
python3 detach_user_policy.py --use-account-id --account account-a --account-id 111111111111 --user user-a --policy-arn arn:aws:iam::111111111111:policy/test-policy
```

グループにポリシー追加:

```bash
python3 attach_group_policy.py --use-account-id --account account-a --account-id 111111111111 --group group-a --policy-arn arn:aws:iam::111111111111:policy/test-policy
```

グループからポリシー削除:

```bash
python3 detach_group_policy.py --use-account-id --account account-a --account-id 111111111111 --group group-a --policy-arn arn:aws:iam::111111111111:policy/test-policy
```

`--policy-file` の代わりに `--policy-json '{"Version":"2012-10-17","Statement":[]}'` のように直接JSONも指定できます。

## ユーザー一覧取得

ユーザー一覧取得は `listuser.py` を使います。

デフォルトは直接指定です。

```bash
python3 listuser.py --use-account-id --account account-a --account-id 111111111111
```

keyログインで一覧取得:

```bash
python3 listuser.py --account account-a --access-key test --secret-key test
```

YAMLから全アカウントを読む:

```bash
python3 listuser.py --config ./config.yaml
```

YAMLから一部アカウントだけ読む:

```bash
python3 listuser.py --config ./config.yaml --account account-a
```

YAMLの `account_id` を使ってmotoのアカウント分離で一覧取得:

```bash
python3 listuser.py --config ./config.yaml --use-account-id
```

## よくあるエラー

### configなしの場合、--user を指定してください

YAMLを使わない直接指定では、作成ユーザーを `--user` で指定してください。

```bash
python3 main.py --use-account-id --account-id 111111111111 --user test-user
```

### --use-account-id を使う場合、--account-id が必要です

直接指定で `--use-account-id` を使う場合は、`--account-id` も指定してください。

```bash
python3 main.py --use-account-id --account-id 111111111111 --user test-user
```

### keyログインの場合、--access-key と --secret-key が必要です

`--use-account-id` を使わない場合は、キーを指定してください。

```bash
python3 main.py --access-key test --secret-key test --user test-user
```

