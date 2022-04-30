import fs from 'fs';
import Parser from 'tree-sitter';
import CppLanguage from 'tree-sitter-cpp';

export const LANGUAGES: {[language: string]: any} = {
  cpp: CppLanguage,
};

export function parseFile(language: string, file: string): Parser.Tree {
  if (!Object.keys(LANGUAGES).includes(language)) {
    throw new Error(`Language ${language} is not supported`);
  }
  const parser = new Parser();
  parser.setLanguage(LANGUAGES[language]);
  return parser.parse(fs.readFileSync(file, 'utf8'));
}
