import fs from 'fs';
import { program } from 'commander';
import { parseFile, LANGUAGES } from './parser';
import path from 'path'

function errorHandler(message: string) {
  console.error(message);
  process.exit(1);
}

function getTokensFromSubmission(submissionFileData: string, language: string) {
  const tree = parseFile(language, submissionFileData);
    
  const cursor = tree.rootNode.walk();

  let tokens = []
  while (true) {
    if (cursor.gotoFirstChild()) {
      continue;
    }
    else {
      if (cursor.nodeType.replace(/\s/g, '').length != 0) { // remove whitespace-only tokens
        tokens.push({
          'char': cursor.startPosition.column + 1,
          'line': cursor.startPosition.row + 1,
          'type': cursor.nodeType,
          'value': cursor.nodeText
        });
      }
    }
    if (cursor.gotoNextSibling()) {
      continue;
    }

    cursor.gotoParent();
    while (!cursor.gotoNextSibling()) {
      if (!cursor.gotoParent()) {
        break;
      }
    }
    if (cursor.currentNode === tree.rootNode) {
      break;
    }
  }
  return tokens;
}

function tokenizeSubmissions(basepath: string) {
  // We assume that this config has already been validated, so we don't care about providing nice
  // error messages for invalid config properties
  const config = JSON.parse(fs.readFileSync(path.join(basepath, 'config.json'), 'utf8'));
  let tokens = getTokensFromSubmission('src/test.cpp', config.language);
}

program
  .command('tokenizer <basepath>')
  .action((basepath: string) => {
    tokenizeSubmissions(basepath);
  });

program.parse(process.argv)
