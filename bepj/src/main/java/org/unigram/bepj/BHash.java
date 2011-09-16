package org.unigram.bepj;

import java.io.Serializable;
import java.util.Collections;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Random;
import java.util.Vector;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

public class BHash implements Serializable {

    // internal variables used in the various calculations                            
	private static Log log = LogFactory.getLog(BHash.class);
	private static final long MAX_VALUE = 0xFFFFFFFFL; 	// max value to limit it to 4 bytes 		

	/** statics. */
	static final int BYTEBLOCK = 8;	
	static final double C_R = 1.3;
	static final int INTBLOCK  = 32;
	static final String KEYEXT = ".key";
	static public final int NOTFOUND = -1;

	private int bn; // number of total buckets (output of NON-minimal perfect hashing)
	private int bn_m; // number of buckets for each hash function
	private long keysLen; // total length of keys
	private Random rnd;
	private int n; // number of keys
	private long seed; // seed for hash functions		

	/** tables. */
	private int[] B;           // store the assigned vertices
	private short[] gtable;    // store g values
	private short[] gtable2;   // store g values in compressed representations
	private int[] levelA;      // store every 256-th rank result
	private short[] levelB;    // store every 32-th rank result
	private long[] strOffsets; // store key's offsets
	private byte[] strTable;   // store original keys in raw format	

	/**
	 * Constructor.
	 */
	public BHash() {
		super();
		this.rnd = new Random();
	}
	
	@SuppressWarnings("unchecked")
	public int build(final Vector<String> keys) {
		this.clear();			

		log.info("Starting build ...");		
		this.n     = keys.size();
		this.bn_m  = (int) (this.n * C_R / 3);
		this.bn    = this.bn_m * 3;

		// main loop                                                                            
		boolean finished = false;
		for (int iter = 0; iter < 20; iter++) {
			int [] edges = new int[this.n*3];
			int [] offset = new int[this.bn+1];
			boolean [] visitedEdges = new boolean[this.n];
			boolean [] visitedVerticies = new boolean[this.bn];
			int [] gtable =  new int[this.bn] ; // vertex marker			
			
			log.info( Integer.toString(iter)+ "-th try ...");
		    this.seed = this.rnd.nextInt();

		    log.info("generateing candidate edges");
		    int [] deg = new int[this.bn];
			Vector<HgEdge> verteces = new Vector<HgEdge>();
			long [] v = new long[3]; 
		    for (int i = 0; i < keys.size(); i++){
		    	int [] iv = new int[3];
		    	this.hash(keys.get(i).getBytes(), this.seed, v);
		        iv[0] = (int) (v[0] % this.bn_m); // get mod (so the value become small!!)
		        iv[1] = (int) (v[1] % this.bn_m) + this.bn_m;
		        iv[2] = (int) (v[2] % this.bn_m) + this.bn_m * 2;
		        verteces.add(new HgEdge(iv));
		        deg[(int) (iv[0])] = deg[(int) (iv[0])]+1;
		        deg[(int) (iv[1])] = deg[(int) (iv[1])]+1;
		        deg[(int) (iv[2])] = deg[(int) (iv[2])]+1;
		    }
		    
		    log.info("checking whether identical edges exist or not");		    
		    //Collections.sort(verteces);

		    boolean edgeSuccess = true;
		    for (int i = 1; i < verteces.size(); i++){
		      if (verteces.get(i-1).equals(verteces.get(i))){
		        log.info("find identical edge\n");
		        edgeSuccess = false;
		        break;
		      }
		    }
		    if (!edgeSuccess) continue;
		    
		    log.info("no identical edge ...");

		    // build offset                                                                       
		    int sum = 0;
		    for (int i = 0; i < this.bn; i++){
		    	offset[i] = sum;
		    	sum += deg[i];
		    }
		    offset[bn] = sum;

		    // build edges                                                                        
		    for (int i = 0; i < bn; i++){ deg[i] = 0; }

		    for (int i = 0; i < n; i++){
		    	for (int j = 0; j < 3; j++){
		    		int e =  offset[(int) verteces.get(i).vertices[j]];
		    		int d =  deg[(int) verteces.get(i).vertices[j]]++;
		    		edges[e+d] = i;
		    	}
		    }
		    
		    // check validity                                                                     
		    for (int i = 0; i < n; i++) { visitedEdges[i] = false; }
		    Queue<Integer> queue = new LinkedList<Integer>();
		    for (int i = 0; i < bn; i++){
		      if (deg[i] == 1) queue.offer((Integer) (edges[offset[i]]));
		      visitedVerticies[i] = false;
		      gtable[i] = 3; // unmarked
		    }
		    
		    int deleteNum = 0;
		    Vector<Pair> extractedEdges = new Vector<Pair>();
		    while (!queue.isEmpty()){
		    	Integer eID = queue.poll(); // edgeID                                             
		        if (visitedEdges[eID.intValue()]) continue;
		        deleteNum++;
		        visitedEdges[eID.intValue()] = true;		

		        final HgEdge e = verteces.get(eID.intValue());
		        int choosed = -1;
		        for (int j = 0; j < 3; j++) {
		            if (--deg[(int) e.vertices[j]] == 1) {
		            	for (int i = (int) offset[(int) e.vertices[j]]; i < offset[ (int) e.vertices[j]+1]; i++){
		                if (!visitedEdges[(int) edges[i]]){
		                  queue.offer(edges[i]);
		                  break;
		                }
		              }
		            } else if (deg[(int)e.vertices[j]] == 0){
		              choosed = j;
		            }
		        }
		        
		        if (choosed == -1){
		            log.warn("unexpected error: we cannot find free vertex\n");
		            break;
		        } 
		        
		        extractedEdges.add(new Pair(eID.intValue(), choosed)); // new pairs
		    }

		    if (deleteNum == n) {
		    	Collections.reverse(extractedEdges);
		        for (int i = 0; i < extractedEdges.size(); i++) {
			    int eid = extractedEdges.get(i).first();
		            final HgEdge edge = verteces.get(eid);
		            final int choosed = extractedEdges.get(i).second();
		            int  val = choosed + 30; // +30: large offsets for limiting positive value
		            for (int j = 0; j < 3; j++){
		                if (!visitedVerticies[(int) edge.vertices[j]]) {
		                    continue;
		                  }
		                  val -= gtable[(int) edge.vertices[j]];		                  
		            }
			        gtable[(int) edge.vertices[choosed]] = val % 3;
			        visitedVerticies[(int) edge.vertices[choosed]] = true;
		        }

		        extractedEdges = null;

		        // set rank table and gtable
		        log.info("set rank table and gtable");
		        this.B  = new int [((bn + INTBLOCK - 1) / INTBLOCK)];
		        this.levelA  = new int [((bn + 256 - 1) / 256)];
		        this.levelB  = new short  [((bn + INTBLOCK - 1)  / INTBLOCK)];
		        this.gtable2 = new short [((bn + 4 - 1) / 4)];
		        int r = 0;
		        for (int i = 0; i < this.bn; i++){
		          if (i % 256 == 0) levelA[i/256] = r;
		          if (i % INTBLOCK == 0) levelB[i/INTBLOCK]  = (short) (r - levelA[i/256]);
		          if (gtable[(int)i] != 3) {
		        	  this.B[i/INTBLOCK] |= (1L << (i%INTBLOCK));
		        	  r++;
		          }
		          gtable2[i/4] |= (gtable[i] << ((i%4)*2));
		        }
		        this.keysLen = 0;
		        for (int i = 0; i < this.n; i++){
		          this.keysLen += keys.get(i).getBytes().length;
		        }
		        this.strTable   = new byte[(int) this.keysLen + 1]; // TODO need to change for big data?
		        log.debug("size of strTable: " + this.strTable.length);
		        this.strOffsets = new long[n+1];

		        Vector<Pair> hashedId2Keys = new Vector<Pair>();
		        for (int i = 0; i < n; i++){
		        	//log.debug("key: " + keys.get(i) 
		        	//		+ "\t hashed value: " 
		        	//		+ this.lookupWocheck(keys.get(i)) + "\n");
		        	hashedId2Keys.add(new Pair((Integer) this.lookupWocheck(keys.get(i)), i)); // new pairs
		        }		        
		        Collections.sort(hashedId2Keys);
		        
		        log.info("making strTable");
		        long lenSum = 0;
		        for (int i = 0; i < n; i++){
		        	this.strOffsets[i] = lenSum;
		        	String str = keys.get(hashedId2Keys.get(i).second());
		        	byte [] strbyte = str.getBytes();
		        	for (int j=0; j < strbyte.length; j++) {
		        		this.strTable[(int) lenSum+j] = strbyte[j];
		        	}
		        	lenSum += str.length();
		        }
		        this.strOffsets[n] = lenSum;
		        finished = true;
		        break;
		    }
		}
		
		if (!finished){
			log.warn("cannot find perfect hash functions\n");
			return -1;
		} else {
			log.info("succeeded to find perfect hash functions\n");
			return 0;			
		}
	}
	
	/**
	 * 
	 * @param buffer
	 * @param initialValue
	 * @return
	 */
	public int[] hash(byte[] buffer, long init, long rnal_v[]) {
		int len, pos;
		//long [] vertexes = new long[3];
		rnal_v[0] = 0x09e3779b9L;
		rnal_v[1] = 0x09e3779b9L;
		rnal_v[2] = init;
		
		// handle most of the key
		pos = 0;
		for (len = buffer.length; len >=12; len -= 12) {
		    rnal_v[0] = add(rnal_v[0], fourByteToLong(buffer, pos));
		    rnal_v[1] = add(rnal_v[1], fourByteToLong(buffer, pos + 4));
		    rnal_v[2] = add(rnal_v[2], fourByteToLong(buffer, pos + 8));
		    hashMix(rnal_v);
		    pos += 12;
		}
		
		rnal_v[2] += buffer.length;
		
		// all the case statements fall through to the next on purpose
		switch(len) {
		case 11:
			rnal_v[2] = add(rnal_v[2], leftShift(byteToLong(buffer[pos + 10]), 24));
		case 10:
			rnal_v[2] = add(rnal_v[2], leftShift(byteToLong(buffer[pos + 9]), 16));
		case 9:
			rnal_v[2] = add(rnal_v[2], leftShift(byteToLong(buffer[pos + 8]), 8));
			// the first byte of internal_v[2] is reserved for the length
		case 8:
			rnal_v[1] = add(rnal_v[1], leftShift(byteToLong(buffer[pos + 7]), 24));
		case 7:
			rnal_v[1] = add(rnal_v[1], leftShift(byteToLong(buffer[pos + 6]), 16));
		case 6:
			rnal_v[1] = add(rnal_v[1], leftShift(byteToLong(buffer[pos + 5]), 8));
		case 5:
			rnal_v[1] = add(rnal_v[1], byteToLong(buffer[pos + 4]));
		case 4:
			rnal_v[0] = add(rnal_v[0], leftShift(byteToLong(buffer[pos + 3]), 24));
		case 3:
			rnal_v[0] = add(rnal_v[0], leftShift(byteToLong(buffer[pos + 2]), 16));
		case 2:
			rnal_v[0] = add(rnal_v[0], leftShift(byteToLong(buffer[pos + 1]), 8));
		case 1:
			rnal_v[0] = add(rnal_v[0], byteToLong(buffer[pos + 0]));
			// case 0: nothing left to add
		}
		hashMix(rnal_v);
		
		int [] vertexes = new int[3];
		vertexes[0] = (int) rnal_v[0];
		vertexes[1] = (int) rnal_v[1];
		vertexes[2] = (int) rnal_v[2];
		return vertexes;
	}

	public long lookup(final String key) {
		  final long id = lookupWocheck(key);
		  final long begin = this.strOffsets[(int) id];
		  final long len = this.strOffsets[(int) (id+1)]-begin;
		  if (key.length() != len) return NOTFOUND;
		  String extractedString = new String(this.strTable, (int) begin, (int) len);
		  if (key.equals(extractedString) == false) {
			  return NOTFOUND;
		  }
		  return id;
	}
	
    public int size() {
		  return (int) n;
	}	
	
	public int lookupWocheck(String string) {
		long [] v = new long[3];
		this.hash(string.getBytes(), this.seed, v);
		  v[0] = (v[0] % bn_m);
		  v[1] = (v[1] % bn_m) + bn_m;
		  v[2] = (v[2] % bn_m) + bn_m * 2;
		  int val = 0;
		  val += lookupGVAL(v[0]);
		  val += lookupGVAL(v[1]);
		  val += lookupGVAL(v[2]);
		  return (int) rank(v[val%3]);
	}

	/**
	 * Do addition and turn into 4 bytes. 
	 */
	private long add(long val, long add) {
		return (val + add) & MAX_VALUE;
	}
	/**
	 * Convert a byte into a long value without making it negative.
	 */
	private long byteToLong(byte b) {
		long val = b & 0x7F;
		if ((b & 0x80) != 0) {
			val += 128;
		}
		return val;
	}

	private void clear(){
		this.B = null;
		this.levelA = null;
		this.levelB = null;
		this.gtable = null;
		this.gtable2 = null;
		this.strOffsets = null;
		this.strTable =null;
	}
	
	/**
	 */
	private long fourByteToLong(byte[] bytes, int offset) {
		return (byteToLong(bytes[offset + 0])
				+ (byteToLong(bytes[offset + 1]) << 8)
				+ (byteToLong(bytes[offset + 2]) << 16)
				+ (byteToLong(bytes[offset + 3]) << 24));
	}
	
	/**
	 * Mix up the values in the hash function.
	 */
	private void hashMix(long [] v) {
	    v[0] = subtract(v[0], v[1]); v[0] = subtract(v[0], v[2]); v[0] = xor(v[0], v[2] >> 13);
	    v[1] = subtract(v[1], v[2]); v[1] = subtract(v[1], v[0]); v[1] = xor(v[1], leftShift(v[0], 8));
	    v[2] = subtract(v[2], v[0]); v[2] = subtract(v[2], v[1]); v[2] = xor(v[2], (v[1] >> 13));
	    v[0] = subtract(v[0], v[1]); v[0] = subtract(v[0], v[2]); v[0] = xor(v[0], (v[2] >> 12));
	    v[1] = subtract(v[1], v[2]); v[1] = subtract(v[1], v[0]); v[1] = xor(v[1], leftShift(v[0], 16));
	    v[2] = subtract(v[2], v[0]); v[2] = subtract(v[2], v[1]); v[2] = xor(v[2], (v[1] >> 5));
	    v[0] = subtract(v[0], v[1]); v[0] = subtract(v[0], v[2]); v[0] = xor(v[0], (v[2] >> 3));
	    v[1] = subtract(v[1], v[2]); v[1] = subtract(v[1], v[0]); v[1] = xor(v[1], leftShift(v[0], 10));
	    v[2] = subtract(v[2], v[0]); v[2] = subtract(v[2], v[1]); v[2] = xor(v[2], (v[1] >> 15));
	 }
	
	/**
	 * Left shift val by shift bits.  Cut down to 4 bytes. 
	 */
	private long leftShift(long val, int shift) {
		return (val << shift) & MAX_VALUE;
	}
	
	private int lookupGVAL(long i) {
		return (this.gtable2[(int) (i/4)] >> ((i&0x3)*2)) & 0x3;
	}
	
	private long rank(long i) {
		return this.levelA[(int) (i/256)] 
		                   + this.levelB[(int) (i/INTBLOCK)] 
		                   + Long.bitCount((this.B[(int) (i/INTBLOCK)] & ((1 << (i%INTBLOCK)) - 1)));
	}
	/**
	 * Do subtraction and turn into 4 bytes. 
	 */
	private long subtract(long val, long subtract) {
		return (val - subtract) & MAX_VALUE;
	}
	/**
	 * Left shift val by shift bits and turn in 4 bytes. 
	 */
	private long xor(long val, long xor) {
		return (val ^ xor) & MAX_VALUE;
	}
}
