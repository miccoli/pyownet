#
# maintain both markdown and reStructuredText README
#
README.txt: README.md
	pandoc --from=markdown --to=rst --output=$@ --reference-links $?
