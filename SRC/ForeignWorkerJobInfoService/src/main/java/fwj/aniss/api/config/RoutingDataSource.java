package fwj.aniss.api.config;

import org.springframework.jdbc.datasource.lookup.AbstractRoutingDataSource;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RoutingDataSource extends AbstractRoutingDataSource {
    private static final Logger LOG = LoggerFactory.getLogger(RoutingDataSource.class);

    @Override
    protected Object determineCurrentLookupKey() {
        boolean isReadOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();
        String ms = isReadOnly ? "slave" : "master";
        LOG.debug("DB Connection isReadOnly::: " + isReadOnly + ", determineCurrentLookupKey::: " + ms);
        return ms;
    }

}