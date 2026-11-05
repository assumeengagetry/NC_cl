#!/bin/zsh
cd -- "${0:A:h}"
for log_file in 日志/*.txt; do
  clear
  printf '%s\n' "当前文件：$log_file" "请将终端窗口放大后截图。本页是已保存的实验日志回显。" ""
  cat -- "$log_file"
  printf '\n截图后按回车，显示下一组日志。'
  read -r reply
done
printf '\n四组日志已显示完毕，可以关闭此窗口。\n'
