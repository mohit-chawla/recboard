# Dev tools for recboard
# Author: Mohit Chawla | mohitchawla.ism@gmail.com

start="#recboard-starts-here" #pattern to start deleting fron
end="#recboard-ends-here" #line with pattern to delete at last
warning="#WARNING do not add your variables in this area"

RBROOT="$HOME/recboard"
REARSERVER="$RBROOT/rear/rear_server.py"
BASH_PROFILE="$HOME/.bash_profile" 

echo "This script require you to clone/move recboard directory in $HOME"
read -p "This script will make changes to or create a $BASH_PROFILE. Proceed? [y/n] " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Run directory tests
echo "Runnning directory tests ..."

if [ ! -d RBROOT ]   # for file "if [-f /home/rama/file]" 
then 
    echo "All good, $RBROOT found"
else
    echo "$RBROOT not present"
fi


if [ -f "$BASH_PROFILE" ]
then
	echo "Making changes to $BASH_PROFILE"
	sed -i -e '/'$start'/,/'$end'/{!p;d;}' $BASH_PROFILE
	echo $start>>$BASH_PROFILE
	echo $warning>>$BASH_PROFILE
	echo "export RBROOT="$RBROOT>>$BASH_PROFILE
	echo " 

	board(){
 		python "$RBROOT"/manage.py runserver
	}

	rear(){
		python "$REARSERVER"
	}

	">>$BASH_PROFILE
	echo $start>>$BASH_PROFILE
	source $BASH_PROFILE
	dollar='$' 
	var_name=(${!RBROOT@})
	echo "
		Hello Human,
		everything configured 
		feel free to use:
		cd $dollar$var_name : go to recboard directory
		rear : start backend server
		board: start django server
	"
else
	echo "No bash_profile found, $BASH_PROFILE"
fi



