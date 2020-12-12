register 'makePairs.py' using jython as myfuncs;

languages = LOAD '/simpledata1.txt' USING JsonLoader('title:chararray, id:chararray, cs:chararray, en:chararray');
B = FOREACH languages GENERATE FLATTEN(myfuncs.createPairs(TOKENIZE(title), TOKENIZE(cs),'cs'));
C = FOREACH languages GENERATE FLATTEN(myfuncs.createPairs(TOKENIZE(title), TOKENIZE(en),'en'));

merged = JOIN C BY words::word FULL OUTER, B BY words::word;
merge = FOREACH merged GENERATE CONCAT((C::words::word IS NOT NULL ? C::words::word : ''), (B::words::word IS NOT NULL ? B::words::word : '')) AS result:chararray;
STORE merge INTO 'hdfs://localhost:9000/table52' USING org.apache.pig.piggybank.storage.CSVExcelStorage();
--DUMP merge
--DESCRIBE merged;
--STORE B INTO 'hdfs://localhost:9000/table1' USING org.apache.pig.piggybank.storage.CSVExcelStorage();
--STORE C INTO 'hdfs://localhost:9000/table1' USING org.apache.pig.piggybank.storage.CSVExcelStorage();
				  