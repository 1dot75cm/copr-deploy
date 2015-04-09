%global with_test 1
%if 0%{?rhel} < 7 && 0%{?rhel} > 0
%global _pkgdocdir %{_docdir}/%{name}-%{version}
%global __python2 %{__python}
%endif

# optional rpm packages
%global with_optional  0

Name:       copr-frontend
Version:    1.56
Release:    2%{?dist}
Summary:    Frontend for Copr

Group:      Applications/Productivity
License:    GPLv2+
URL:        https://fedorahosted.org/copr
# Source is created by
# git clone https://git.fedorahosted.org/git/copr.git
# cd copr/frontend
# tito build --tgz
Source0:    https://git.fedorahosted.org/cgit/copr.git/snapshot/%{name}-%{version}-1.tar.xz

BuildArch:  noarch
BuildRequires: asciidoc
BuildRequires: libxslt
BuildRequires: util-linux
BuildRequires: python-setuptools
BuildRequires: python-requests
BuildRequires: python2-devel
BuildRequires: systemd
%if 0%{?rhel} < 7 && 0%{?rhel} > 0
BuildRequires: python-argparse
%endif
#for doc package
BuildRequires: epydoc
BuildRequires: graphviz

Requires:   httpd
Requires:   mod_wsgi
Requires:   passwd
Requires:   python-alembic
Requires:   python-flask
Requires:   python-flask-openid
Requires:   python-flask-wtf
Requires:   python-flask-sqlalchemy
Requires:   python-flask-script
Requires:   python-flask-whooshee
#Requires:   python-virtualenv
Requires:   python-blinker
Requires:   python-markdown
Requires:   python-psycopg2
Requires:   python-pylibravatar
Requires:   python-whoosh >= 2.5.3
Requires:   pytz
Requires:   python-six
Requires:   python-netaddr
# for tests:
Requires:   pytest
Requires:   python-flexmock
Requires:   python-mock
Requires:   python-decorator
Requires:   yum
%if 0%{?with_optional}
Requires:   logstash
%endif
Requires:   redis
Requires:   python-redis
Requires:   python-dateutil
%if 0%{?rhel} < 7 && 0%{?rhel} > 0
BuildRequires: python-argparse
%endif
# check
BuildRequires: python-six
BuildRequires: python-flask
BuildRequires: python-flask-script
BuildRequires: python-flask-sqlalchemy
BuildRequires: python-flask-openid
BuildRequires: python-flask-whooshee
BuildRequires: python-pylibravatar
BuildRequires: python-flask-wtf
BuildRequires: python-netaddr
BuildRequires: python-redis
BuildRequires: python-dateutil
BuildRequires: pytest
BuildRequires: yum
BuildRequires: python-flexmock
BuildRequires: python-mock
BuildRequires: python-decorator
BuildRequires: python-markdown
BuildRequires: python-alembic
BuildRequires: pytz

%description
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latests builds.

This package contains frontend.

%package doc
Summary:    Code documentation for COPR
Obsoletes:  copr-doc < 1.38

%description doc
COPR is lightweight build system. It allows you to create new project in WebUI,
and submit new builds and COPR will create yum repository from latests builds.

This package include documentation for COPR code. Mostly useful for developers
only.

%prep
%setup -q -n %{name}-%{version}-1


%build
# build documentation
pushd frontend/documentation
make %{?_smp_mflags} python
popd

%install

pushd frontend
install -d %{buildroot}%{_sysconfdir}/copr
install -d %{buildroot}%{_datadir}/copr/coprs_frontend
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store/associations
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store/nonces
install -d %{buildroot}%{_sharedstatedir}/copr/data/openid_store/temp
install -d %{buildroot}%{_sharedstatedir}/copr/data/whooshee
install -d %{buildroot}%{_sharedstatedir}/copr/data/whooshee/copr_user_whoosheer

cp -a coprs_frontend/* %{buildroot}%{_datadir}/copr/coprs_frontend
sed -i "s/__RPM_BUILD_VERSION/%{version}-%{release}/" %{buildroot}%{_datadir}/copr/coprs_frontend/coprs/templates/layout.html

mv %{buildroot}%{_datadir}/copr/coprs_frontend/coprs.conf.example ../
mv %{buildroot}%{_datadir}/copr/coprs_frontend/config/* %{buildroot}%{_sysconfdir}/copr
rm %{buildroot}%{_datadir}/copr/coprs_frontend/CONTRIBUTION_GUIDELINES
touch %{buildroot}%{_sharedstatedir}/copr/data/copr.db

install -d %{buildroot}%{_var}/log/copr
install -d %{buildroot}%{_sysconfdir}/logrotate.d
%if 0%{?with_optional}
install -d %{buildroot}%{_sysconfdir}/logstash.d
cp -a conf/logstash.conf %{buildroot}%{_sysconfdir}/logstash.d/copr_frontend.conf
%endif
cp -a conf/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
touch %{buildroot}%{_var}/log/copr/frontend.log

%check
%if %{with_test} && "%{_arch}" == "x86_64"
    pushd frontend/coprs_frontend
    rm -rf /tmp/copr.db /tmp/whooshee || :
    COPR_CONFIG="$(pwd)/config/copr_unit_test.conf" ./manage.py test
    popd
%endif

%pre
getent group copr-fe >/dev/null || groupadd -r copr-fe
getent passwd copr-fe >/dev/null || \
useradd -r -g copr-fe -G copr-fe -d %{_datadir}/copr/coprs_frontend -s /bin/bash -c "COPR frontend user" copr-fe
/usr/bin/passwd -l copr-fe >/dev/null

%post
service httpd condrestart
%if 0%{?with_optional}
service logstash condrestart
%endif

%files
%license frontend/LICENSE
%doc coprs.conf.example
%dir %{_datadir}/copr
%dir %{_sysconfdir}/copr
%dir %{_sharedstatedir}/copr
%{_datadir}/copr/coprs_frontend

%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%if 0%{?with_optional}
%config(noreplace) %{_sysconfdir}/logstash.d/copr_frontend.conf
%endif

%defattr(-,copr-fe,copr-fe,-)
%dir %{_sharedstatedir}/copr/data
%dir %{_sharedstatedir}/copr/data/openid_store
%dir %{_sharedstatedir}/copr/data/whooshee
%dir %{_sharedstatedir}/copr/data/whooshee/copr_user_whoosheer

%ghost %{_sharedstatedir}/copr/data/copr.db

%defattr(644,copr-fe,copr-fe,755)
%dir %{_var}/log/copr
%ghost %{_var}/log/copr/*.log

%defattr(600,copr-fe,copr-fe,700)
%config(noreplace)  %{_sysconfdir}/copr/copr.conf
%config(noreplace)  %{_sysconfdir}/copr/copr_devel.conf
%config(noreplace)  %{_sysconfdir}/copr/copr_unit_test.conf

%files doc
%license frontend/LICENSE
%doc frontend/documentation/python-doc

%changelog
* Sat Mar 07 2015 mosquito <sensor.wen@gmail.com> 1.56-2
- Rebuild for copr.fdzh.org

* Fri Mar 06 2015 Valentin Gologuzov <vgologuz@redhat.com> 1.56-1
- hotfix:#1199258]  Link to Source RPM on build detail page points to a wrong URL

* Fri Mar 06 2015 mosquito <sensor.wen@gmail.com> 1.55-2
- Rebuild for copr.fdzh.org

* Mon Mar 02 2015 Valentin Gologuzov <vgologuz@redhat.com> 1.55-1
- [frontend] fix tests to be runnable without redis-server.

* Mon Mar 02 2015 Valentin Gologuzov <vgologuz@redhat.com> 1.54-1
- [backend] [rhbz:#1091640] RFE: Release specific additional repos
- [frontend][backend] [rhbz:#1119300]  [RFE] allow easy add copr repos in using
  repository lis
- [frontend] enabled `gpgcheck=1` in .repo template
- [copr] monitor page redone: show version for each chroot
- [frontend] [rhbz:#1160370, #1173165] sub-page on resubmit action, where user
  could change preselected build chroots.
- [frontend] added filelog for frontend
- [frontend] Added "-%%{release}" to the build version on the copr pages.
- mark license as license in spec
- [rhbz:#1171796] copr sometimes doesn't delete build from repository
- [backend] [rhbz:#1073333] Record consecutive builds fails to redis. Added
  script to produce warnings for nagios check from failures recorded to redis.

* Thu Feb 05 2015 Valentin Gologuzov <vgologuz@redhat.com> 1.53-1
- [frontend] enabled `gpgcheck=1` in .repo template
- [frontend] correct url for pubkey in .repo

* Fri Jan 23 2015 Valentin Gologuzov <vgologuz@redhat.com> 1.52-1
- add url to gpg pubkey in .repo files
- [rhbz:#1183702]  Interrupted builds aren't re-added to the
  builder queue, and stuck forever in RUNNING state.
- [rhbz:#1133650] RFE: copr frontend on page of build details,
  results section should show multiple links that link directly for every
  chroot directory
- UI to control `enable_net` option, DB schema changes
- new command AddDebugUser for manage script
- [RHBZ:#1176364] Wrong value for the build timeout.
- [RHBZ:#1177179] Display the timezone with a format more similar to
  ISO 8601

* Mon Dec 15 2014 Valentin Gologuzov <vgologuz@redhat.com> 1.51-1
- bugfix: send correct chroots in on_auto_createrepo_change()
- control auto_createrepo property of project through API

* Thu Dec 11 2014 Valentin Gologuzov <vgologuz@redhat.com> 1.50-1
- fix unittest

* Thu Dec 11 2014 Valentin Gologuzov <vgologuz@redhat.com> 1.49-1
- api workaround: removed auto_createrepo option
- show copr-frontend version;
- re-enabling of auto_createrepo should produce createrepo action
- 1169366 - Files installed in both copr-frontend and copr-frontend-doc
- Fix mismatch between documentation and actual API in new build
- disabled debug prints, fixed PEP8 violations

* Mon Nov 24 2014 Valentin Gologuzov <vgologuz@redhat.com> 1.48-1
- [frontend] fixed paramater validation for API hanlde `create_new_copr`
- [frontend] show "createrepo" action only when user disable auto_createrepo
- [frontend] removed hardcoded frontend url from /api page.

* Fri Oct 24 2014 Valentin Gologuzov <vgologuz@redhat.com> 1.47-1
- [frontend] sending createrepo action
- [frontend] [html]  new option to configure copr->auto_creatrepo
- [fronted] adding option to disable auto invokation of createrepo
- [frontent] [WIP]fixing unittest, better isolation during test run
- [frontend] [RHBZ: #1149091] bugfix:  'Repeat' does not respect chroot
  selection of original build
- Added script to automate tests execution inside virtualenv
- [frontend] [RHBZ:#1146825] Reorder chroots for monitor widget

* Wed Sep 24 2014 Valentin Gologuzov <vgologuz@redhat.com> 1.46-1
- [frontend] added helper function and flask filter which allows to ensure that
  url starts with either http or https, see config

* Thu Sep 18 2014 Miroslav Suchý <msuchy@redhat.com> 1.45-1
- revert f0e5c211f86cc3691fda8d4412c21ef6338a339f
- [frontend] including project name
- [frontend] recent builds on the home page
- [frontend] project search update after patch
- support for kerberos authentication
- do not strictly resist on Fedora's OpenID
- [frontend] recent builds sorting fix
- [frontend] user's recent builds on their home page

* Wed Aug 27 2014 Miroslav Suchý <msuchy@redhat.com> 1.44-1
- fix spec parsing on arm
-  'manage.py update_indexes' and search fix
- [RHBZ:1131286] RFE: API endpoint for a project's "monitor" status

* Mon Aug 25 2014 Adam Samalik <asamalik@redhat.com> 1.43-1
- [frontend] bugfix: context_processor shouldn't return None
- [frontend] task queue sorting fix

* Fri Aug 22 2014 Adam Samalik <asamalik@redhat.com> 1.42-1
- [frontend] make all html tags to have the same left-padding
- [frontend][RHBZ:1128602] RFE: define banner for local instance
- [frontend][RHBZ:1131186] Use https URLs to install copr repo file
- [frontend] [RHBZ:1128231] Show list of recent builds owned by user ( for
  logged in users).
- [API] friendly notification about invalid/expired token
- [frontend] project name can not be just number
- [frontend] starting builds highlighted on the waiting list
- [frontend] [BZ:1128231] RFE: frontend user interface like koji: added
  `/recent` page which list of ended builds.
- [frontend] fixed SQLa ordering queries.
- [frontend] paginator fix
- [frontend] build states list
- [frontend] minor bugfix: fixed api method `cancel build`.

* Wed Aug 13 2014 Miroslav Suchý <msuchy@redhat.com> 1.41-1
- [frontend] bugifx: for some projects API doesn't return last-modified time in
  detail resource.
- new queue for backend
- [frontend] new waiting queue
- [frontend] sorting packages on the Monitor view

* Tue Jul 22 2014 Miroslav Suchý <msuchy@redhat.com> 1.40-1
- [frontend] status page fix
- [frontend] How to enable a repo on a Overview page
- [frontend] build listing fix
- [frontend] status page extension - running tasks
- [frontend] modified chroots in overview
- FrontendCallback prettified
- Starting state implemented, cancelling fixed
- [frontend] new build status: Starting
- [frontend] db migration

* Tue Jul 15 2014 Miroslav Suchý <msuchy@redhat.com> 1.39-1
- frontend: add f21 chroot
- 1118829 - suggest owners to entry link to reporting web
- small changes after review
- better and safer deleting of builds
- [frontend] build's ended_on time fix
- [frontend] built pkgs info - include subpackages
- deleting of failed builds fixed
- [frontend] api build details extended
- pkg name on the build page
- [frontend] pkg version on the Monitor page
- [frontend] pkg name and version on the build page
- [frontend] pkg name and version support
- [frontend] skipped state support
- Ansible playbok to generate frontend db documentation
- obsolete copr-doc
- [frontend] repeat build button in all states of build except pending
- [frontend] project update by admin fix
- get rid of multi assigment
- [frontend] repofiles without specifying architecture
- api search fix
- WSGIPassAuthorization needs to be on

* Fri May 30 2014 Miroslav Suchý <msuchy@redhat.com> 1.38-1
- [frontend] running build can not be deleted
- [frontend] cancel status set to all chroots

* Fri May 30 2014 Miroslav Suchý <msuchy@redhat.com> 1.37-1
- [frontend] monitor table design unified
- [frontend] skipping bad package urls
- builders can delete their builds
- css fix

* Wed May 21 2014 Miroslav Suchý <msuchy@redhat.com> 1.36-1
- 1077794 - add LICENSE to -doc subpackage
- 1077794 - own /usr/share/doc/copr-frontend
- 1077794 - remove BR make
- 1077794 - require passwd

* Wed May 21 2014 Miroslav Suchý <msuchy@redhat.com> 1.35-1
- build detail and new builds table
- admin/playground page
- Use "https" in API template
- Use flask_openid safe_roots to mitigate Covert Redirect.
- add newline at the end of repo file
- [cli & api] delete a project

* Thu Apr 24 2014 Miroslav Suchý <msuchy@redhat.com> 1.34-1
- add indexes
- 1086729 - make build tab friendly for users without JS
- copr-cli cancel fix
- correctly print chroots
- [frontend] SEND_EMAILS config correction

* Tue Apr 15 2014 Miroslav Suchý <msuchy@redhat.com> 1.33-1
- api: add chroots to playground api call
- check if chroot exist for specified project
- better explain additional yum repos

* Thu Apr 10 2014 Miroslav Suchý <msuchy@redhat.com> 1.32-1
- send permissions request to admin not to requestee

* Wed Apr 09 2014 Miroslav Suchý <msuchy@redhat.com> 1.31-1
- validate chroots in POST requests with API
- add /playground/list/ api call
- add playground column to copr table
- Make repo urls nicer so that last part matches filename
- fixes and documentation for 66287cc8
- use https for gravatar urls
- We can choose chroots for new builds
- [frontend] delete all builds with their project
- [frontend] config comments
- [frontend] sending emails when perms change
- [frontend] typo s/Coper/Copr/
- api: fix coprs.models.User usage in search
- status page fix: long time
- status page fix: project's owner
- building pkgs separately
- [frontend] let apache log in default location
- api: fix KeyError in search

* Wed Mar 19 2014 Miroslav Suchý <msuchy@redhat.com> 1.30-1
- Fix typo in API doc HTML
- white background
- status page
- create _pkgdocdir

* Tue Mar 18 2014 Miroslav Suchý <msuchy@redhat.com> 1.29-1
- move frontend to standalone package

* Thu Feb 27 2014 Miroslav Suchý <msuchy@redhat.com> 1.28-1
- [backend] - pass lock to Actions

* Wed Feb 26 2014 Miroslav Suchý <msuchy@redhat.com> 1.27-1
- [frontend] update to jquery 1.11.0
- [fronted] link username to fas
- [cli] allow to build into projects of other users
- [backend] do not create repo in destdir
- [backend] ensure that only one createrepo is running at the same time
- [cli] allow to get data from sent build
- temporary workaround for BZ 1065251
- Chroot details API now uses GET instead of POST
- when deleting/canceling task, go to same page
- add copr modification to web api
- 1063311 - admin should be able to delete task
- [frontend] Stray end tag h4.
- [frontend] another s/coprs/projects/ rename
- [frontend] provide info about last successfull build
- [spec] rhel5 needs group definition even in subpackage
- [frontend] move 'you agree' text to dd
- [frontend] add margin to chroots-set
- [frontend] add margin to field label
- [frontend] put disclaimer to paragraph tags
- [frontend] use black font color
- [frontend] use default filter instead of *_not_filled
- [frontend] use markdown template filter
- [frontend] use isdigit instead of is_int
- [frontend] move Serializer to helpers
- [frontend] fix coding style and py3 compatibility
- [cli] fix coding style and py3 compatibility
- [backend] fix coding style and py3 compatibility

* Tue Jan 28 2014 Miroslav Suchý <miroslav@suchy.cz> 1.26-1
- lower testing date
- move localized_time into filters
- [frontend] update user data after login
- [frontend] use iso-8601 date

* Mon Jan 27 2014 Miroslav Suchý <msuchy@redhat.com> 1.25-1
- 1044085 - move timezone modification out of template and make it actually
  work
- clean up temp data if any
- [db] timezone can be nullable
- [frontend] actually save the timezone to model
- fix colision of revision id
- 1044085 - frontend: display time in user timezone
- [frontend] rebuild stuck task
- disable test on i386
- use experimental createrepo_c to get rid of lock on temp files
- [frontend] - do not throw ISE when build_id is malformed
- [tests] add test for BuildLogic.add
- [tests] add test for build resubmission
- [frontend] permission checking is done in BuildLogic.add
- [frontend] remove BuildLogic.new, use BL.add only
- [api] fix validation error handling
- [cli] fix initial_pkgs and repos not sent to backend
- [frontend] fix BuildsLogic.new not assigning copr to build
- [frontend] allow resubmitting builds from monitor
- [frontend] allow GET on repeat_build
- [frontend] 1050904 - monitor shows not submitted chroots
- [frontend] rename active_mock_chroots to active_chroots
- [frontend] rename MockChroot.chroot_name to .name
- [frontend] 1054474 - drop Copr.build_count nonsense
- [tests] fix https and repo generation
- [tests] return exit code from manage.py test
- 1054472 - Fix deleting multiple SRPMs
- [spec] tighten acl on copr-be.conf
- [backend] - add missing import
- 1054082 - general: encode to utf8 if err in mimetext
- [backend] lock log file before writing
- 1055594 - mockremote: always unquote pkg url
- 1054086 - change vendor tag
- mockremote: rawhide instead of $releasever in repos when in rawhide chroot
- 1055499 - do not replace version with $releasever on rawhide
- 1055119 - do not propagate https until it is properly signed
- fix spellings on chroot edit page
- 1054341 - be more verbose about allowed licenses
- 1054594 - temporary disable https in repo file

* Thu Jan 16 2014 Miroslav Suchý <msuchy@redhat.com> 1.24-1
- add BR python-markdown
- [fronted] don't add description to .repo files
- [spec] fix with_tests conditional
- add build deletion
- 1044158 - do not require fas username prior to login
- replace http with https in copr-cli and in generated repo file
- [cli] UX changes - explicitely state that pkgs is URL
- 1053142 - only build copr-cli on el6
- [frontend] correctly handle mangled chroot
- [frontend] do not traceback when user malform url
- [frontend] change default description and instructions to sound more
  dangerously
- 1052075 - do not set chroots on repeated build
- 1052071 - do not throw ISE when copr does not exist

* Mon Jan 13 2014 Miroslav Suchý <msuchy@redhat.com> 1.23-1
- [backend] rhel7-beta do not have comps
- 1052073 - correctly parse malformed chroot

* Fri Jan 10 2014 Miroslav Suchý <msuchy@redhat.com> 1.22-1
- [backend] if we could not spawn VM, wait a moment and try again
- [backend] use createrepo_c instead of createrepo
- 1050952 - check if copr_url exist in config
- [frontend] replace newlines in description by space in repo file

* Wed Jan 08 2014 Miroslav Suchý <msuchy@redhat.com> 1.21-1
- 1049460 - correct error message
- [cron] manualy clean /var/tmp after createrepo

* Wed Jan 08 2014 Miroslav Suchý <msuchy@redhat.com> 1.20-1
- [cli] no need to set const with action=store_true
- [cli] code cleanup
- 1049460 - print nice error when projects does not exist
- 1049392 - require python-setuptools
- [backend] add --verbose to log to stderr
- [backend] handle KeyboardInterrupt without tons of tracebacks
- 1048508 - fix links at projects lists
- [backend] in case of error the output is in e.output
- [selinux] allow httpd to search
- [backend] set number of worker in name of process
- [logrotate] rotate every week unconditionally
- [backend] do not traceback if jobfile is mangled
- [backend] print error messages to stderr
- [cli] do not require additional arguments for --nowait
- [backend] replace procname with setproctitle
- [cli] use copr.fedoraproject.org as default url
- [frontend] show monitor even if last build have been canceled
- [backend] call correct function
- [cli] print errors to stderr
- 1044136 - do not print TB if config in mangled
- 1044165 - Provide login and token information in the same form as entered to
  ~/.config-copr
- [frontend] code cleanup
- [frontend] move rendering of .repo file to helpers
- 1043649 - in case of Fedora use $releasever in repo file
- [frontend] condition should be in reverse

* Mon Dec 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.19-1
- [backend] log real cause if ansible crash
- [frontend] try again if whoosh does not get lock
- [backend] if frontend does not respond, repeat
- print yum repos nicely
- Bump the copr-cli release to 0.2.0 with all the changes made
- Refer to the man page for more information about the configuration file for
  copr-cli
- Rework the layout of the list command
- Fix parsing the copr_url from the configuration file
- [backend] run createrepo as copr user
- 1040615 - wrap lines with long URL

* Wed Dec 11 2013 Miroslav Suchý <msuchy@redhat.com> 1.18-1
- [frontend] inicialize variable

* Wed Dec 11 2013 Miroslav Suchý <msuchy@redhat.com> 1.17-1
- [frontend] fix latest build variable overwrite

* Wed Dec 11 2013 Miroslav Suchý <msuchy@redhat.com> 1.16-1
- [backend] store jobs in id-chroot.json file
- [frontend] handle unknown build/chroot status
- use newstyle ansible variables

* Tue Dec 10 2013 Miroslav Suchý <msuchy@redhat.com> 1.15-1
- [frontend] smarter package name parsing
- [frontend] extend range to allow 0
- handle default timeout on backend
- initial support for SCL
- [backend] create word readable files in result directory
- [backend] print tracebacks
- [frontend] monitor: display only pkg name w/o version
- [doc] update api docs
- [doc] update copr-cli manpage
- [cli] list only name, description and instructions
- [cli] add support for build status & build monitor
- [frontend] add build status to API
- [playbook] do not overwrite mockchain
- [backend] add spece between options
- [backend] pass mock options correctly
- [frontend] support markdown in description and instructions
- [backend] Add macros to mockchain define arguments
- [backend] Pass copr username and project name to MockRemote
- [backend] Handle additional macro specification in MockRemote
- [frontend] monitor: show results per package
- [frontend] add favicon
- [backend] quote strings before passing to mockchain
- send chroots with via callback to frontend
- [cli] change cli to new api call
- enhance API documentation
- add yum_repos to coprs/user API call
- [frontend] provide link to description of allowed content
- [backend] we pass just one chroot
- [backend] - variable play is not defined
- if createrepo fail, run it again
- [cron] fix syntax error
- [man] state that --chroot for create command is required
- [spec] enable tests
- [howto] add note about upgrading db schema
- [frontend]: add copr monitor
- [tests]: replace test_allowed_one
- [tests]: fix for BuildChroots & new backend view
- [frontend] rewrite backend view to use Build <-> Chroot relation
- [frontend] add Build <-> Chroot relation
- 1030493 - [cli] check that at least one chroot is entered
- [frontend] typo
- fixup! [tests]: fix test_build_logic to handle BuildChroot
- fixup! [frontend] add ActionsLogic
- [tests]: fix test_build_logic to handle BuildChroot
- [spec] enable/disable test using variable
- add migration script - add table build_chroot
- [frontend] skip legal-flag actions when dumping waiting actions
- [frontend] rewrite backend view to use Build <-> Chroot relation
- [frontend] add ActionsLogic
- [frontend] create BuildChroot objects on new build
- [frontend] add Build <-> Chroot relation
- [frontend] add StatusEnum
- [frontend] fix name -> coprname typo
- [frontend] remove unused imports
- [frontend] add missing json import
- [backend] rework ip address extraction
- ownership of /etc/copr should be just normal
- [backend] - wrap up returning action in "action" blok
- [backend] rename backend api url
- [backend] handle "rename" action
- [backend] handle "delete" action
- base handling of actions
- move callback to frontend to separate object
- secure waiting_actions with password
- pick only individual builds
- make address, where we send legal flags, configurable
- send email to root after legal flag have been raised

* Fri Nov 08 2013 Miroslav Suchý <msuchy@redhat.com> 1.14-1
- 1028235 - add disclaimer about repos
- fix pagination
- fix one failing test

* Wed Nov 06 2013 Miroslav Suchý <msuchy@redhat.com> 1.13-1
- suggest correct name of repo file
- we could not use releasever macro
- no need to capitalize Projects
- another s/copr/project
- add link to header for sign-in
- fix failing tests
- UX - let textarea will full widht of box
- UX - make background of hovered builds darker
- generate yum repo for each chroot of copr
- align table header same way as ordinary rows
- enable resulting repo and disable gpgchecks

* Mon Nov 04 2013 Miroslav Suchý <msuchy@redhat.com> 1.12-1
- do not send parameters when we neither need them nor use them
- authenticate using api login, not using username
- disable editing name of project
- Add commented out WTF_CSRF_ENABLED = True to configs
- Use new session for each test
- fix test_coprs_general failures
- fix test_coprs_builds failures
- Add WTF_CSRF_ENABLED = False to unit test config
- PEP8 fixes
- Fix compatibility with wtforms 0.9
- typo s/submited/submitted/
- UX - show details of build only after click
- add link to FAQ to footer
- UX - add placeholders
- UX - add asterisk to required fields
- dynamicly generate url for home
- add footer

* Sat Oct 26 2013 Miroslav Suchý <msuchy@redhat.com> 1.11-1
- catch IOError from libravatar if there is no network

* Fri Oct 25 2013 Miroslav Suchý <msuchy@redhat.com> 1.10-1
- do not normalize url
- specify full prefix of http
- execute playbook using /usr/bin/ansible-playbook
- use ssh transport
- check after connection is made
- add notes about debuging mockremote
- clean up instance even when worker fails
- normalize paths before using
- do not use exception variable
- operator should be preceded and followed by space
- remove trailing whitespace
- convert comment to docstring
- use ssh transport
- do not create new ansible connection, reuse self.conn
- run copr-be.py as copr
- s/Copr/Project/ where we use copr in meaning of projects
- number will link to those coprs, to which it refers
- run log and jobgrab as copr user
- log event to log file
- convert comment into docstring
- use unbufferred output for copr-be.py
- hint how to set ec2 variables
- document sleeptime
- document copr_url for copr-cli
- document how to set api key for copr-cli
- do not create list of list
- document SECRET_KEY variable
- make note how to become admin
- instruct people to install selinux with frontend

* Thu Oct 03 2013 Miroslav Suchý <msuchy@redhat.com> 1.9-1
- prune old builds
- require python-decorator
- remove requirements.txt
- move TODO-backend to our wiki
- create pid file in /var/run/copr-backend
- add backend service file for systemd
- remove daemonize option in config
- use python logging
- create pid file in /var/run by default
- do not create destdir
- use daemon module instead of home brew function
- fix default location of copr-be.conf
- 2 tests fixed, one still failing
- fix failing test test_fail_on_missing_dash
- fixing test_fail_on_nonexistent_copr test
- run frontend unit tests when building package
- Adjust URLs in the unit-tests to their new structure
- Adjust the CLI to call the adjuste endpoint of the API
- Adjust API endpoint to reflects the UI endpoints in their url structure
- First pass at adding fedmsg hooks.

* Tue Sep 24 2013 Miroslav Suchý <msuchy@redhat.com> 1.8-1
- 1008532 - require python2-devel
- add note about ssh keys to copr-setup.txt
- set home of copr user to system default

* Mon Sep 23 2013 Miroslav Suchý <msuchy@redhat.com> 1.7-1
- 1008532 - backend should own _pkgdocdir
- 1008532 - backend should owns /etc/copr as well
- 1008532 - require logrotate
- 1008532 - do not distribute empty copr.if
- 1008532 - use %%{?_smp_mflags} macro with make
- move jobsdir to /var/lib/copr/jobs
- correct playbooks path
- selinux with enforce can be used for frontend

* Wed Sep 18 2013 Miroslav Suchý <msuchy@redhat.com> 1.6-1
- add BR python-devel
- generate selinux type for /var/lib/copr and /var/log/copr
- clean up backend setup instructions
- initial selinux subpackage

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.5-1
- 1008532 - use __python2 instead of __python
- 1008532 - do not mark man page as doc
- 1008532 - preserve timestamp

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.4-1
- add logrotate file

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.3-1
- be clear how we create tgz

* Mon Sep 16 2013 Miroslav Suchý <msuchy@redhat.com> 1.2-1
- fix typo
- move frontend data into /var/lib/copr
- no need to own /usr/share/copr by copr-fe
- mark application as executable
- coprs_frontend does not need to be owned by copr-fe
- add executable attribute to copr-be.py
- remove shebang from dispatcher.py
- squeeze description into 80 chars
- fix typo
- frontend need argparse too
- move results into /var/lib/copr/public_html
- name of dir is just copr-%%version
- Remove un-necessary quote that breaks the tests
- Adjust unit-tests to the new urls
- Update the URL to be based upon a /user/copr/<action> structure
- comment config copr-be.conf and add defaults
- put examples of builderpb.yml and terminatepb.yml into doc dir
- more detailed description of copr-be.conf
- move files in config directory not directory itself
- include copr-be.conf
- include copr-be.py
- create copr with lighttpd group
- edit backend part of copr-setup.txt
- remove fedora16 and add 19 and 20
- create -doc subpackage with python documentation
- add generated documentation on gitignore list
- add script to generate python documentation
- copr-setup.txt change to for mock
- rhel6 do not know _pkgdocdir macro
- make instruction clear
- require recent whoosh
- add support for libravatar
- include backend in rpm
- add notes about lighttpd config files and how to deploy them
- do not list file twice
- move log file to /var/log
- change destdir in copr-be.conf.example
- lightweight is the word and buildsystem has more meaning than 'koji'.
- restart apache after upgrade of frontend
- own directory where backend put results
- removal of hidden-file-or-dir
  /usr/share/copr/coprs_frontend/coprs/logic/.coprs_logic.py.swo
- copr-backend.noarch: W: spelling-error %%description -l en_US latests ->
  latest, latest's, la tests
- simplify configuration - introduce /etc/copr/copr*.conf
- Replace "with" statements with @TransactionDecorator decorator
- add python-flexmock to deps of frontend
- remove sentence which does not have meaning
- change api token expiration to 120 days and make it configurable
- create_chroot must be run as copr-fe user
- add note that you have to add chroots to db
- mark config.py as config so it is not overwritten during upgrade
- own directory data/whooshee/copr_user_whoosheer
- gcc is not needed
- sqlite db must be owned by copr-fe user
- copr does not work with selinux
- create subdirs under data/openid_store
- suggest to install frontend as package from copr repository
- on el6 add python-argparse to BR
- add python-requests to BR
- add python-setuptools to BR
- maintain apache configuration on one place only
- apache 2.4 changed access control
- require python-psycopg2
- postgresql server is not needed
- document how to create db
- add to HOWTO how to create db
- require python-alembic
- add python-flask-script and python-flask-whooshee to requirements
- change user in coprs.conf.example to copr-fe
- fix paths in coprs.conf.example
- copr is noarch package
- add note where to configure frontend
- move frontend to /usr/share/copr/coprs_frontend
- put production placeholders in coprs_frontend/coprs/config.py
- put frontend into copr.spec
- web application should be put in /usr/share/%%{name}

* Mon Jun 17 2013 Miroslav Suchý <msuchy@redhat.com> 1.1-1
- new package built with tito


