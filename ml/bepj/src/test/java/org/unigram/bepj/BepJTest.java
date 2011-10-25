package org.unigram.bepj;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.util.Random;
import java.util.Vector;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

import junit.framework.TestCase;

public class BepJTest extends TestCase {
	
	private String serializedPath = "bepj-serialized.txt";
	
	public void testBuild() throws ClassNotFoundException {
	    	Random rnd = new Random();
	    	BepJ<Integer> bepj = new BepJ<Integer>();
	    	try {
	    		FileReader in = new FileReader(this.inputPath);
	    		BufferedReader br = new BufferedReader(in);
	    		String line;
	    		Vector<String> keys = new Vector<String>();
	    		Vector<Integer> values = new Vector<Integer>();
	    		int i = 0; 
	    		while ((line = br.readLine()) != null) {
	    			keys.add(line);
	    			values.add(new Integer(i));
	    			i+=1;
	    		}
	    		bepj.build(keys, values);
	    		Integer number = bepj.get("surrendering");
	    		log.debug("number of surrendering: " + number);
	    		
	    		log.debug("began serialization");
	    		FileOutputStream outFile = new FileOutputStream(this.serializedPath ); 
	    		ObjectOutputStream outObject = new ObjectOutputStream(outFile);
	    		outObject.writeObject(bepj);
	    		log.debug("finished serialization");
	    		
	    		log.debug("begin deserialization");
	    		FileInputStream inFile = new FileInputStream(this.serializedPath);
	    		ObjectInputStream inObject = new ObjectInputStream(inFile);
	    		BepJ newBepj = (BepJ) inObject.readObject();
	    		int newId = (Integer) newBepj.get("surrendering");
	    		log.debug("bepj newId of surrendering: " + newId);
	    		log.debug("finished deserialization");	    		
	    		
	    		br.close();
	    		in.close();
	    	} catch (IOException e) {
	    		log.warn(e);
	    	}
	    }	 
	
	    private String inputPath  = "sample.txt";
	    private static Log log = LogFactory.getLog(BepJTest.class);	    
	    
}
