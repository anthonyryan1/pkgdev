import os
import subprocess

from pkgcheck import reporters, scan
from pkgcore.repository import errors as repo_errors
from snakeoil.cli import arghparse


push = arghparse.ArgumentParser(
    prog='pkgdev push', description='run QA checks on commits and push them')
push.add_argument(
    'remote', nargs='?', default='origin',
    help='remote git repository (default: origin)')
push.add_argument(
    'refspec', nargs='?', default='master',
    help='destination ref to update (default: master)')
push.add_argument(
    '-f', '--force', action='store_true',
    help='forcibly push commits with QA errors')
push.add_argument(
    '-n', '--dry-run', action='store_true',
    help='pretend to push the commits')


@push.bind_main_func
def _push(options, out, err):
    # determine repo
    try:
        repo = options.domain.find_repo(
            os.getcwd(), config=options.config, configure=False)
    except (repo_errors.InitializationError, IOError) as e:
        push.error(str(e))

    # scan commits for QA issues
    pipe = scan(['--exit', '--commits'])
    with reporters.FancyReporter(out) as reporter:
        for result in pipe:
            reporter.report(result)

    # fail on errors unless force pushing
    if pipe.errors:
        with reporters.FancyReporter(out) as reporter:
            out.write(out.bold, out.fg('red'), '\nFAILURES', out.reset)
            for result in sorted(pipe.errors):
                reporter.report(result)
        if not options.force:
            return 1

    git_args = []
    if repo.repo_id == 'gentoo':
        # gentoo repo requires signed pushes
        git_args.append('--signed')
    if options.dry_run:
        git_args.append('--dry-run')

    git_args.extend([options.remote, options.refspec])

    # push commits upstream
    try:
        subprocess.run(
            ['git', 'push'] + git_args,
            cwd=repo.location, check=True,
            stderr=subprocess.PIPE, encoding='utf8')
    except FileNotFoundError:
        push.error('git not found')
    except subprocess.CalledProcessError as e:
        error = e.stderr.splitlines()[0]
        push.error(error)

    return 0