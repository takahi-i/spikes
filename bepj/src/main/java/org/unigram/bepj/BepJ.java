package org.unigram.bepj;

import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

public class BepJ<ValueType extends Serializable> implements Serializable {

	/** logger. */
	private static Log log = LogFactory.getLog(BepJ.class);

	public static final int MAXWORKSIZE = 1048576;

	/** tables. */
	private BHash _bh;

	private Vector<ValueType> _values;

	private Map<String, ValueType> _work;

	public BepJ() {
		super();
		this._bh = new BHash();
		this._values = null;
		this._work = new HashMap<String, ValueType>();
	}
	
	private void build() {
		// TODO Auto-generated method stub
	}
	
	public int build(Vector<String> keys, Vector<ValueType> vals) {
		if (keys.size() != vals.size()) {
			log.warn("keys.size: " + keys.size() + " != vals.size: "
					+ vals.size());
			return -1;
		}

		if (this._bh.build(keys) == -1) {
			return -1;
		}

		if (this._values != null)
			this._values = null;
		this._values = new Vector<ValueType>(vals.size());
		for (int i = 0; i < vals.size(); i++) {
			this._values.add(null);
		}

		for (int i = 0; i < vals.size(); i++) {
			int hid = _bh.lookupWocheck(keys.get(i));
			this._values.set(hid, vals.get(i));
		}
		return 0;
	}

	public ValueType get(final String key) {
		int id = 0;
		
		if (this._bh.size() != 0 && (id = (int) this._bh.lookup(key)) != BHash.NOTFOUND) {
			System.out.println("hashed id :" + id);
			return this._values.get(id);
		}

		ValueType result = _work.get(key);
		if (result != null) {
			return result;
		} else {
			if (_work.size() == MAXWORKSIZE) {
				this.build(); // merge _work and _bh
			}
			return null;
		}
	}
}
