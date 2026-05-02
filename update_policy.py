import argparse

import iamcli_common
import iamfunction


def main():
    parser = argparse.ArgumentParser()
    iamcli_common.add_account_args(parser)
    parser.add_argument('--policy-arn')
    parser.add_argument('--policy-name')
    parser.add_argument('--policy-json')
    parser.add_argument('--policy-file')
    args = parser.parse_args()

    def process_account(account, iam):
        if args.policy_arn or args.policy_name:
            targets = [{'policy_name': args.policy_name}]
        else:
            targets = iamcli_common.get_config_list(account, 'update_policies')

        if len(targets) == 0:
            print('更新対象ポリシーなし')
            return

        for target in targets:
            if isinstance(target, str):
                target = {'policy_name': target}

            try:
                policy_arn = iamcli_common.get_policy_arn(
                    account,
                    cli_policy_arn=args.policy_arn,
                    policy_name=target.get('policy_name') or target.get('name'),
                    config_value=target,
                )
                policy_document = iamcli_common.load_policy_document(
                    account,
                    args,
                    target,
                )
            except ValueError as e:
                print('入力エラー: ' + str(e))
                return

            result = iamfunction.update_policy(policy_arn, policy_document, iam)
            print(result['Note'])
            print('VersionId: ' + result['VersionId'])
            if len(result['DeletedVersions']) == 0:
                print('削除した古いバージョンなし')
            else:
                print('削除した古いバージョン: ' + ', '.join(result['DeletedVersions']))

    if not args.config and not args.policy_arn:
        print('入力エラー: configなしの場合、--policy-arn を指定してください')
        return

    iamcli_common.run_for_accounts(args, process_account)


if __name__ == '__main__':
    main()
