#!/bin/bash
#
# ARG_POSITIONAL_SINGLE([admin-pass],[Password for the "admin" superuser that GraphDB creates. If running the first-time user setup, this will be the password set for the admin. The admin user will only be used to create and modify permissions of other database users.])
# ARG_OPTIONAL_SINGLE([env-file-path],[],[Path to a .env file containing environment variables for Neurobagel node configuration.],[.env])
# ARG_OPTIONAL_BOOLEAN([run-user-setup],[],[Whether or not to run the first-time GraphDB setup steps, including changing the admin password and creating a new database user.],[on])
# ARG_HELP([Run first-time user setup for a new GraphDB instance and/or set up a new GraphDB graph database. This script will automatically create a GraphDB configuration file (data-config.ttl) for your newly created database in your current directory. For more information, see https://neurobagel.org/infrastructure/.])
# ARGBASH_GO()
# needed because of Argbash --> m4_ignore([
### START OF CODE GENERATED BY Argbash v2.9.0 one line above ###
# Argbash is a bash code generator used to get arguments parsing right.
# Argbash is FREE SOFTWARE, see https://argbash.io for more info
# Generated online by https://argbash.io/generate


die()
{
	local _ret="${2:-1}"
	test "${_PRINT_HELP:-no}" = yes && print_help >&2
	echo "$1" >&2
	exit "${_ret}"
}


begins_with_short_option()
{
	local first_option all_short_options='h'
	first_option="${1:0:1}"
	test "$all_short_options" = "${all_short_options/$first_option/}" && return 1 || return 0
}

# THE DEFAULTS INITIALIZATION - POSITIONALS
_positionals=()
# THE DEFAULTS INITIALIZATION - OPTIONALS
_arg_env_file_path=".env"
_arg_run_user_setup="on"


print_help()
{
	printf '%s\n' "Run first-time user setup for a new GraphDB instance and/or set up a new GraphDB graph database. This script will automatically create a GraphDB configuration file (data-config.ttl) for your newly created database in your current directory. For more information, see https://neurobagel.org/infrastructure/."
	printf 'Usage: %s [--env-file-path <arg>] [--(no-)run-user-setup] [-h|--help] <admin-pass>\n' "$0"
	printf '\t%s\n' "<admin-pass>: Password for the \"admin\" superuser that GraphDB creates. If running the first-time user setup, this will be the password set for the admin. The admin user will only be used to create and modify permissions of other database users."
	printf '\t%s\n' "--env-file-path: Path to a .env file containing environment variables for Neurobagel node configuration. (default: '.env')"
	printf '\t%s\n' "--run-user-setup, --no-run-user-setup: Whether or not to run the first-time GraphDB setup steps, including changing the admin password and creating a new database user. (on by default)"
	printf '\t%s\n' "-h, --help: Prints help"
}


parse_commandline()
{
	_positionals_count=0
	while test $# -gt 0
	do
		_key="$1"
		case "$_key" in
			--env-file-path)
				test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
				_arg_env_file_path="$2"
				shift
				;;
			--env-file-path=*)
				_arg_env_file_path="${_key##--env-file-path=}"
				;;
			--no-run-user-setup|--run-user-setup)
				_arg_run_user_setup="on"
				test "${1:0:5}" = "--no-" && _arg_run_user_setup="off"
				;;
			-h|--help)
				print_help
				exit 0
				;;
			-h*)
				print_help
				exit 0
				;;
			*)
				_last_positional="$1"
				_positionals+=("$_last_positional")
				_positionals_count=$((_positionals_count + 1))
				;;
		esac
		shift
	done
}


handle_passed_args_count()
{
	local _required_args_string="'admin-pass'"
	test "${_positionals_count}" -ge 1 || _PRINT_HELP=yes die "FATAL ERROR: Not enough positional arguments - we require exactly 1 (namely: $_required_args_string), but got only ${_positionals_count}." 1
	test "${_positionals_count}" -le 1 || _PRINT_HELP=yes die "FATAL ERROR: There were spurious positional arguments --- we expect exactly 1 (namely: $_required_args_string), but got ${_positionals_count} (the last one was: '${_last_positional}')." 1
}


assign_positional_args()
{
	local _positional_name _shift_for=$1
	_positional_names="_arg_admin_pass "

	shift "$_shift_for"
	for _positional_name in ${_positional_names}
	do
		test $# -gt 0 || break
		eval "$_positional_name=\${1}" || die "Error during argument parsing, possibly an Argbash bug." 1
		shift
	done
}

parse_commandline "$@"
handle_passed_args_count
assign_positional_args 1 "${_positionals[@]}"

# OTHER STUFF GENERATED BY Argbash

### END OF CODE GENERATED BY Argbash (sortof) ### ])
# [ <-- needed because of Argbash

set -euo pipefail

# Reassign command line args to more readable named variables
ENV_FILE_PATH=$_arg_env_file_path
ADMIN_PASS=$_arg_admin_pass
RUN_USER_SETUP=$_arg_run_user_setup

# Set the environment variables in the shell, to use in the script
source "${ENV_FILE_PATH}"
echo "Environment variables have been set from ${ENV_FILE_PATH}."

# Extract just the database name
DB_NAME="${NB_GRAPH_DB#repositories/}"
NB_GRAPH_PORT_HOST=${NB_GRAPH_PORT_HOST:-7200}

# Get the directory of this script to be able to find the data-config_template.ttl file
SCRIPT_DIR=$(dirname "$0")

echo "The GraphDB server is being accessed at http://localhost:${NB_GRAPH_PORT_HOST}."

##### First time GraphDB setup #####

if [ "${RUN_USER_SETUP}" = "on" ]; then
    echo "First time GraphDB user setup enabled."

    # 1. Change database admin password
    echo "Changing the admin password (note: if you have previously set the admin password, this has no effect)..."
	# TODO: To change a *previously set* admin password, we need to also provide the current password via -u
    curl -X PATCH --header 'Content-Type: application/json' http://localhost:${NB_GRAPH_PORT_HOST}/rest/security/users/admin -d "{\"password\": \""${ADMIN_PASS}"\"}"
    
	# 2. If security is not enabled, enable it (i.e. allow only authenticated users access)
	is_security_enabled=$(curl -s -X GET http://localhost:${NB_GRAPH_PORT_HOST}/rest/security)
	if [ "${is_security_enabled}" = "false" ]; then
		echo "Enabling password-based access control to all databases ..."
		# NOTE: This command fails without credentials once security is enabled
		curl -X POST --header 'Content-Type: application/json' -d true http://localhost:${NB_GRAPH_PORT_HOST}/rest/security
	else
		echo "Password-based access control has already been enabled."
	fi

    # 3. Create a new database user
	# TODO: Separate this out from the first-time setup? As this can technically be run at any time to create additional users.
	# NOTE: If user already exists, response will be "An account with the given username already exists." OK for script.
	echo "Creating a new database user ${NB_GRAPH_USERNAME}..."
    curl -X POST --header 'Content-Type: application/json' -u "admin:${ADMIN_PASS}" -d @- http://localhost:${NB_GRAPH_PORT_HOST}/rest/security/users/${NB_GRAPH_USERNAME} <<EOF
    {
        "username": "${NB_GRAPH_USERNAME}",
        "password": "${NB_GRAPH_PASSWORD}"
    } 
EOF
fi


##### Database setup #####

# 4. Create and save custom configuration file for the new database
# TODO: Should we add a suffix to data-config.ttl for the db name?
echo "Creating a GraphDB configuration file (./data-config.ttl) for the new database ${DB_NAME}..."
sed 's/rep:repositoryID "my_db" ;/rep:repositoryID "'"${DB_NAME}"'" ;/' ${SCRIPT_DIR}/data-config_template.ttl > data-config.ttl

# 5. Create a new database
# Assumes data-config.ttl is in the same directory as this script!
echo "Creating the GraphDB database ${DB_NAME}..."
curl -X PUT -u "admin:${ADMIN_PASS}" http://localhost:${NB_GRAPH_PORT_HOST}/${NB_GRAPH_DB} --data-binary "@data-config.ttl" -H "Content-Type: application/x-turtle"

# 6. Grant newly created user access permission to the database
# Confirm user wants to proceed with changing user permissions
# while true; do
# 	read -p "WARNING: We will now give ${NB_GRAPH_USERNAME} read/write access to ${NB_GRAPH_DB}. This operation will REPLACE any existing permissions you have granted to user ${NB_GRAPH_USERNAME}, including any access to other databases. ${NB_GRAPH_USERNAME} may lose access to other databases as a result. Proceed? (y/n) " yn
# 	case $yn in
# 		[Yy]* ) break;;
# 		[Nn]* ) echo "Exiting..."; exit;;
# 		* ) echo "Please answer y or n.";;
# 	esac
# done

echo "Granting user ${NB_GRAPH_USERNAME} read/write permissions to database ${DB_NAME}..."
curl -X PUT --header 'Content-Type: application/json' -d "
{\"grantedAuthorities\": [\"WRITE_REPO_${DB_NAME}\",\"READ_REPO_${DB_NAME}\"]}" http://localhost:${NB_GRAPH_PORT_HOST}/rest/security/users/${NB_GRAPH_USERNAME} -u "admin:${ADMIN_PASS}"

echo "Done."

# ] <-- needed because of Argbash
