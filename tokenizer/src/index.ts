import fs from 'fs';
import { program } from 'commander';
import { parseFile } from './parser';

function errorHandler(message: string) {
  console.error(message);
  process.exit(1);
}

function tokenizeSubmissions() {

}

program
  .command('tokenizer <basepath>')
  .action((basepath: string) => {
    const tree = parseFile(language, file);


  });

program.parse(process.argv);
