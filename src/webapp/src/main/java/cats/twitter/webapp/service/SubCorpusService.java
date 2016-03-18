package cats.twitter.webapp.service;

import java.io.IOException;
import java.io.Writer;
import java.util.Optional;

import cats.twitter.model.SubCorpus;
import cats.twitter.model.User;

/**
 * Created by Hicham.
 */
public interface SubCorpusService
{
	SubCorpus createSubCorpus(long corpusId, String name, Optional<String> regexp, Optional<String[]> hashtags,
		Optional<String[]> mentions);

	public SubCorpus getSubCorpus(long subId);

	void exportCSV(User user, long id, Writer writer) throws IOException;
}
