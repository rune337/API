import argparse
import json

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--policy-arn')
    parser.add_argument('--policy-name')
    parser.add_argument('--version-id')
    args = parser.parse_args()

    def process_account(account, iam):
        try:
            policy_arn = iamcli_common.get_policy_arn(
                account,
                cli_policy_arn=args.policy_arn,
                policy_name=args.policy_name,
            )
        except ValueError as e:
            print('入力エラー: ' + str(e))
            return

        result = iamfunction.get_policy_document(
            policy_arn,
            iam,
            args.version_id,
        )

        print('PolicyName: ' + result['PolicyName'])
        print('PolicyArn: ' + result['PolicyArn'])
        print('VersionId: ' + result['VersionId'])
        print(json.dumps(result['Document'], ensure_ascii=False, indent=2))

    if not args.config and not args.policy_arn:
        print('入力エラー: configなしの場合、--policy-arn を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
