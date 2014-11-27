#!/bin/sh

php fetch_answer_by_user.php "wang-xiao-chi"
sleep 100

for i in {1..500}
do
    php fetch_user_by_question.php
    php fetch_answer_by_user.php
   echo "Welcome $i times"
done
