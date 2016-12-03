module Main where

import System.Environment (getArgs)
import System.IO (FilePath)
import System.FilePath
import System.Directory (getDirectoryContents, doesDirectoryExist)
import Control.Monad (foldM, filterM, mapM, liftM2)
import Data.Function.Memoize (memoize2)

import Text.ParserCombinators.Parsec


levenshtein :: [Char] -> [Char] -> Int
levenshtein [] yy = length yy
levenshtein xx [] = length xx
levenshtein xx@(x:xs) yy@(y:ys) 
    | x  == y   = levenshtein' xs ys
    | otherwise = 1 + (minimum [levenshtein' xx ys, levenshtein' xs yy, levenshtein' xs ys])

levenshtein' = memoize2 levenshtein

-- | Some measure on how much the first arg is far from being a substring of the second.
sublev :: [Char] -> [Char] -> Int
sublev [] yy = 0
sublev xx [] = length xx
sublev xx@(x:xs) yy@(y:ys) 
    | x  == y   = sublev' xs ys
    | otherwise = minimum [sublev' xx ys, 1 + (sublev' xs yy), 1 + (sublev' xs ys)]
sublev' = memoize2 sublev



allDirectoryChildren :: FilePath -> IO [FilePath]
allDirectoryChildren f = do
    d <- doesDirectoryExist f 
    directChildren <- fmap  (filter (\x -> x /= "." && x /= "..")) (getDirectoryContents f)
    let directChildren' = map ((</>) f) directChildren
    directoryChildren <- filterM doesDirectoryExist directChildren'
    allChildrenList <- mapM allDirectoryChildren directoryChildren
    return $ directChildren' ++ (concat allChildrenList)


data Parsed = Link String (Maybe String)
            | Reference String String
            | Refered String String
            | FootRef String
            | FootRefd String String
            | AllElse String
    deriving (Show, Eq)

wellBal :: Char -> Char -> GenParser Char st String
wellBal c d = 
    try (do {y <- many $ noneOf [c,d]; char c; x <- wellBal c d; char d; z <- many $ noneOf [c,d]; return $ y ++ [c] ++ x ++ [d] ++ z}) 
    <|> (many $ noneOf [c,d])

wellBalBracket = wellBal '[' ']'
wellBalParen = wellBal '(' ')'

parseInBrackets :: GenParser Char st String
parseInBrackets = do
    char '['
    text <- wellBalBracket
    char ']'
    return text

parseLinkRef :: GenParser Char st String
parseLinkRef = do
    char '('
    text <- wellBalParen 
    char ')'
    return text

parseLink :: GenParser Char st Parsed
parseLink = do
    text <- parseInBrackets 
    url <- optionMaybe parseLinkRef
    return $ Link text url

parseReference :: GenParser Char st Parsed
parseReference = do
    text <- parseInBrackets
    char '['
    ref <- many (noneOf "[]")
    char ']'
    return $ Reference text ref

parseRefered :: GenParser Char st Parsed
parseRefered = do
    char '['
    ref <-  many (noneOf "[]")
    char ']'
    char ':'
    text <- many (noneOf "\n")
    return $ Refered ref text

parseFootRef :: GenParser Char st Parsed
parseFootRef = do
    char '['
    char '^'
    ref <- many (noneOf "[]") 
    char ']'
    return $ FootRef ref 
 
parseFootRefd :: GenParser Char st Parsed
parseFootRefd = do
    char '['
    char '^'
    ref <- many (noneOf "[]")
    char ']'
    char ':'
    text <- many (noneOf "\n") 
    return $ FootRefd ref text  

parseAllElse :: GenParser Char st Parsed
parseAllElse = do
    text <- many1 (noneOf "[")
    return $ AllElse text


parseAll :: GenParser Char st [Parsed]
parseAll = do
    all <- many $ choice $ map try [parseReference, 
                                    parseRefered, 
                                    parseFootRef, 
                                    parseFootRefd, 
                                    parseLink,
                                    parseAllElse]
    eof
    return all

actuallyParse :: String -> Either ParseError [Parsed]
actuallyParse input = parse parseAll "(unknown)" input


main = do
    root <- fmap (!! 0) getArgs
    print $ actuallyParse root 
    
    


