import fs from 'fs';
import { program } from 'commander';
import { parseFile, LANGUAGES } from './parser';

function errorHandler(message: string) {
  console.error(message);
  process.exit(1);
}

function tokenizeSubmissions() {

}

program
  .command('tokenizer <basepath>')
  .action((basepath: string) => {
    const tree = parseFile('cpp', '../src/test.cpp');
    
    const cursor = tree.rootNode.walk();
    while (true) {
      if (cursor.gotoFirstChild() || cursor.gotoNextSibling()) {
        console.log(cursor.nodeType);
        continue;
      }
      cursor.gotoParent();
      let hadSibling = true;
      while (!cursor.gotoNextSibling()) {
        if (!cursor.gotoParent()) {
          hadSibling = false;
          break;
        }
      }
      console.log('===> ', cursor.nodeType);
      if (cursor.currentNode === tree.rootNode) {
        break;
      }
    }
    
  });

program.parse(process.argv)
