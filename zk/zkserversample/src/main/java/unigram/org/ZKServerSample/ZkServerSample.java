package org.unigram.zk;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

import org.apache.zookeeper.CreateMode;
import org.apache.zookeeper.WatchedEvent;
import org.apache.zookeeper.Watcher;
import org.apache.zookeeper.ZooKeeper;
import org.apache.zookeeper.ZooDefs.Ids;
import org.apache.zookeeper.server.ZooKeeperServerMain;
import org.apache.zookeeper.server.quorum.QuorumPeerConfig.ConfigException;

public class ZkServerSample {

    public static class MainThread extends Thread {
        final File confFile;
        final TestZKSMain main;

        public MainThread(int clientPort) throws IOException {
            super("Standalone server with clientPort:" + clientPort);
            File tmpDir = new File("conf");
            confFile = new File(tmpDir, "zoo.cfg");

            FileWriter fwriter = new FileWriter(confFile);
            fwriter.write("tickTime=2000\n");
            fwriter.write("initLimit=10\n");
            fwriter.write("syncLimit=5\n");

            File dataDir = new File(tmpDir, "data");
            
            // Convert windows path to UNIX to avoid problems with "\"
            String dir = dataDir.toString();
            String osname = java.lang.System.getProperty("os.name");
            if (osname.toLowerCase().contains("windows")) {
                dir = dir.replace('\\', '/');
            }
            fwriter.write("dataDir=" + dir + "\n");
            
            fwriter.write("clientPort=" + clientPort + "\n");
            fwriter.flush();
            fwriter.close();

            main = new TestZKSMain();
        }

        public void run() {
            String args[] = new String[1];
            args[0] = confFile.toString();
            try {
                main.initializeAndRun(args);
            } catch (Exception e) {
                // test will still fail even though we just log/ignore
            }
        }

        public void shutdown() {
            main.shutdown();
        }
    }

    public static  class TestZKSMain extends ZooKeeperServerMain {
        
        protected void initializeAndRun(String[] args) throws ConfigException, IOException {
            super.initializeAndRun(args);
        }       

        public void shutdown() {
            super.shutdown();
        }
    }

    public static void main(String argv[]) {
        final int CLIENT_PORT = 3181;
        try {
            MainThread main = new MainThread(CLIENT_PORT);
            main.start();
            main.shutdown();
        } catch (Exception e) {
            System.out.println("Exception: " + e);
        }

    }

    
}

