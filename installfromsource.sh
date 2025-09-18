#!/usr/bin/env bash

echo ""
echo "*** Installing devtoolbox from source ....."
# check whether flatpak-builder was installed or not if it's not installed exit the installation
if [ -z $(command -v "flatpak-builder") ]
then
    echo "flatpk-builder application is not installed. Install using your package manager !!"
   echo "*** Exiting the installation !!"
   exit 1
else
    # creating a repo and build directory if they doesn't exists
    if [ ! -d ./repo ]
    then
        echo "*** Creating a repository folder called repo ...."
        `mkdir ./repo`
    else
        rm -rf ./repo
        mkdir ./repo
    fi
    if [ ! -d ./build ]
    then
        echo "*** Creating a build folder called build ...."
        `mkdir ./build`
    else
        rm -rf ./build
        mkdir ./build
    fi
fi
echo "*** Building the application using devtoolbox json ....."
flatpak-builder --repo=./repo --force-clean --user ./build me.iepure.devtoolbox.json
if [[ "$(flatpak remotes --user --columns=name | awk '{ print $1 }' | grep "devtoolbox")" == "devtoolbox" ]]
then
    echo ""
    echo "*** devtoolbox repo already exits, removing and re-adding the repo ..."
    flatpak uninstall --delete-data me.iepure.devtoolbox --assumeyes
    flatpak remote-delete devtoolbox
    echo ""
fi
echo "*** Adding the repository named devtoolbox using the repo folder ...."
flatpak remote-add --user devtoolbox ./repo --no-gpg-verify
echo "*** Installing the devtoolbox application for ther user using devtoolbox repo ...." 
flatpak install --user devtoolbox me.iepure.devtoolbox --assumeyes
echo "*** Installation complete !!"
echo "*** Running flatpak ....."
flatpak run me.iepure.devtoolbox 