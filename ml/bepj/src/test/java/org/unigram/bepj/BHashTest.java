package org.unigram.bepj;

import junit.framework.TestCase;
import java.io.*;
import java.util.Random;
import java.util.Vector;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

public class BHashTest extends TestCase {

    public BHashTest(String name) {
        super(name);
    }

    public void testHash() {
    	Random rnd = new Random();
    	BHash bob = new BHash();
    	try {
    		FileReader in = new FileReader(this.inputPath);
    		BufferedReader br = new BufferedReader(in);
    		String line;
    		int i = 0;
    		while ((line = br.readLine()) != null) {
    			if (i >100) {break;}
    			long seed = rnd.nextInt(10);
    			long [] v = new long[3];
    			bob.hash(line.getBytes(), seed, v);
    			for (int j = 0; j<3; j++) {
    				assertTrue(v[j] >= 0);
    			}
    			i += 1;
    		}
    		br.close();
    		in.close();
    	} catch (IOException e) {
    		log.warn(e);
    	}
    }

    public void testBuild() throws ClassNotFoundException {
    	BHash bob = new BHash();
    	try {
    		FileReader in = new FileReader(this.inputPath);
    		BufferedReader br = new BufferedReader(in);
    		String line;
    		Vector<String> keys = new Vector<String>();
    		while ((line = br.readLine()) != null) {
    			keys.add(line);
    		}
    		
    		assertTrue(bob.build(keys) == 0);
    		long id1 = bob.lookup(this.testString);
    		assertTrue(id1 != BHash.NOTFOUND);
    		long id2 = bob.lookup(this.noExistString);
    		assertTrue(id2 == BHash.NOTFOUND);
    		
    		br.close();
    		in.close();
    	} catch (IOException e) {
    		log.warn(e);
    	}
    }
    
    public void testLookupWocheck() throws ClassNotFoundException {
    	BHash bob = new BHash();
    	try {
    		FileReader in = new FileReader(this.inputPath);
    		BufferedReader br = new BufferedReader(in);
    		String line;
    		Vector<String> keys = new Vector<String>();
    		while ((line = br.readLine()) != null) {
    			keys.add(line);
    		}
    		br.close();
    		in.close();    		
    		assertTrue(bob.build(keys) == 0);
    		log.info("keys.size:" + keys.size());
    		for (int i =0; i<keys.size(); i++) {
    			int val = bob.lookupWocheck(keys.get(i));
    			assertTrue( (keys.size() >= val && val >= 0));
    		}
    	} catch (IOException e) {
    		log.warn(e);
    	}
    }
    
    
    public void testSerializtion() throws ClassNotFoundException {
    	BHash bob = new BHash();
    	try {
    		FileReader in = new FileReader(this.inputPath);
    		BufferedReader br = new BufferedReader(in);
    		String line;
    		Vector<String> keys = new Vector<String>();
    		while ((line = br.readLine()) != null) {
    			keys.add(line);
    		}
    		br.close();
    		in.close();    		
    		assertTrue(bob.build(keys) == 0);

    		long id1 = bob.lookup(this.testString);
    		assertTrue(id1 != BHash.NOTFOUND);
    		long id2 = bob.lookup(this.noExistString);
    		assertTrue(id2 == BHash.NOTFOUND);
    		
    		log.debug("began serialization");
    		FileOutputStream outFile = new FileOutputStream(this.serializedPath); 
    		ObjectOutputStream outObject = new ObjectOutputStream(outFile);
    		outObject.writeObject(bob);
    		log.debug("finished serialization");
    		
    		log.debug("begin deserialization");
    		FileInputStream inFile = new FileInputStream(this.serializedPath);
    		ObjectInputStream inObject = new ObjectInputStream(inFile);
    		BHash newbob = (BHash) inObject.readObject();

    		long newId1 = newbob.lookup(this.testString);
    		assertTrue(id1 == newId1);

    		long newId2 = newbob.lookup(this.noExistString);
    		assertTrue(newId2 == BHash.NOTFOUND);    		
    		
    		log.debug("finished deserialization");    		
    	} catch (IOException e) {
    		log.warn(e);
    	}
    }    

    private String inputPath  = "sample.txt";	
    private String serializedPath = "serizalized.txt";
    private String testString = "surrendering";
    private String noExistString = "surrrrrendering";
    private static Log log = LogFactory.getLog(BHashTest.class);

}
