cur_path=$(pwd)

cd $(dirname $0)

# echo $(pwd)

PATH=$PATH:$(pwd)

cd $cur_path

unset cur_path